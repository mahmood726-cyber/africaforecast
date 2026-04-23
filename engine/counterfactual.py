# sentinel:skip-file — hardcoded paths / templated placeholders are fixture/registry/audit-narrative data for this repo's research workflow, not portable application configuration. Same pattern as push_all_repos.py and E156 workbook files.
"""
Counterfactual simulation engine — do-operator Layer 4.

Implements Pearl's do-operator by:
  1. Estimating OLS coefficients from lagged panel data per (child, parent) edge
  2. Forward-simulating from last observed values
  3. Clamping intervened variables (linearly interpolated to target over horizon)
  4. Propagating effects to causal children in topological order
  5. Quantifying uncertainty via Monte Carlo draws

Public API
----------
simulate_counterfactual(panel, dag, indicators, countries, intervention, ...)
    -> CounterfactualResult

precompute_intervention_grid(panel, dag, indicators, countries, grid_spec, ...)
    -> dict[str, CounterfactualResult]

interpolate_intervention(grid, indicator, magnitude, country)
    -> pd.DataFrame
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from engine.causal_graph import topological_sort, get_children
from engine.config import SEED


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class CounterfactualResult:
    """Container for a counterfactual simulation result."""

    baseline: pd.DataFrame
    """Forward simulation with NO intervention (business-as-usual)."""

    counterfactual: pd.DataFrame
    """Forward simulation WITH intervention applied."""

    intervention: dict
    """The intervention specification: {indicator_id: magnitude}."""

    intervention_type: str
    """How magnitude is applied: "multiply" or "add"."""

    affected_indicators: List[str]
    """Indicators whose trajectories differ from baseline (direct + causal children)."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _estimate_ols_coefficients(
    panel: pd.DataFrame,
    dag: dict,
    indicators: List[str],
) -> Dict[str, Dict[str, float]]:
    """
    Estimate OLS regression coefficient beta_{child ~ parent} from lagged panel.

    For each (child, parent) edge in dag, regress:
        child[t] ~ parent[t-1]  (simple single-lag OLS)

    Returns
    -------
    coefs : {child: {parent: beta}}
    """
    coefs: Dict[str, Dict[str, float]] = {}

    for child, parents in dag.items():
        if child not in panel.columns:
            continue
        coefs[child] = {}
        for parent, _source, sign in parents:
            if parent not in panel.columns:
                continue

            # Build (y, x) pairs: y = child[t], x = parent[t-1], per country
            y_vals, x_vals = [], []
            for iso3, grp in panel.groupby("iso3"):
                grp_sorted = grp.sort_values("year")
                y = grp_sorted[child].values[1:]
                x = grp_sorted[parent].values[:-1]
                mask = np.isfinite(x) & np.isfinite(y)
                y_vals.extend(y[mask])
                x_vals.extend(x[mask])

            y_arr = np.array(y_vals, dtype=float)
            x_arr = np.array(x_vals, dtype=float)

            if len(x_arr) < 3:
                # Fallback: use sign from DAG
                coefs[child][parent] = float(sign) * 0.05
                continue

            # OLS: beta = cov(x,y) / var(x), anchored to DAG sign
            x_c = x_arr - x_arr.mean()
            y_c = y_arr - y_arr.mean()
            var_x = float(np.dot(x_c, x_c))
            if var_x < 1e-12:
                coefs[child][parent] = float(sign) * 0.05
            else:
                beta = float(np.dot(x_c, y_c) / var_x)
                # Honour the causal sign direction from the DAG
                if sign != 0 and beta * sign < 0:
                    beta = abs(beta) * sign
                coefs[child][parent] = beta

    return coefs


def _last_observed(panel: pd.DataFrame, countries: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Return the most recent observed value per (country, indicator).

    Returns
    -------
    last : {iso3: {indicator: value}}
    """
    last: Dict[str, Dict[str, float]] = {}
    for iso3 in countries:
        grp = panel[panel["iso3"] == iso3]
        if grp.empty:
            last[iso3] = {}
            continue
        row = grp.sort_values("year").iloc[-1]
        last[iso3] = {col: float(row[col]) for col in row.index
                      if col not in ("iso3", "year") and pd.notna(row[col])}
    return last


def _clamp_value(
    base_val: float,
    magnitude: float,
    step: int,
    horizon: int,
    intervention_type: str,
) -> float:
    """
    Return the intervened value at simulation step `step` (1-indexed, 1..horizon).

    Linearly interpolates from base_val toward target over the horizon.
    """
    frac = step / horizon  # 0 at start, 1 at end

    if intervention_type == "multiply":
        target = base_val * magnitude
    elif intervention_type == "add":
        target = base_val + magnitude
    else:
        target = base_val * magnitude  # default

    return base_val + frac * (target - base_val)


def _forward_simulate(
    panel: pd.DataFrame,
    dag: dict,
    indicators: List[str],
    countries: List[str],
    horizon: int,
    interventions: Optional[Dict[str, float]] = None,
    intervention_type: str = "multiply",
    n_draws: int = 200,
    rng: Optional[np.random.Generator] = None,
) -> pd.DataFrame:
    """
    Forward-simulate indicator trajectories for each country.

    For each future year (1..horizon), updates indicators in topological order:
    - Intervened indicators: clamped to linearly interpolated target.
    - Other indicators: updated via OLS coefficients + Gaussian noise.

    Monte Carlo draws (n_draws) quantify uncertainty.

    Returns
    -------
    pd.DataFrame with columns:
        iso3, year, {ind}_mean, {ind}_lo80, {ind}_hi80
        for each indicator present in panel.
    """
    if rng is None:
        rng = np.random.default_rng(SEED)

    if interventions is None:
        interventions = {}

    # Estimate coefficients
    coefs = _estimate_ols_coefficients(panel, dag, indicators)

    # Topological order (parents before children)
    topo_order = topological_sort(dag)
    # Keep only indicators we actually have
    avail_inds = [ind for ind in topo_order if ind in panel.columns and ind in indicators]
    # Also include indicators in our list not in the DAG (exogenous)
    in_topo = set(topo_order)
    exog = [ind for ind in indicators if ind not in in_topo and ind in panel.columns]
    process_order = avail_inds + exog

    # Get last observed state per country
    last_obs = _last_observed(panel, countries)

    # Estimate per-indicator residual std from panel (for noise draws)
    ind_std: Dict[str, float] = {}
    for ind in indicators:
        if ind not in panel.columns:
            continue
        vals = panel[ind].dropna().values
        if len(vals) > 1:
            # Use std of year-on-year changes within country
            changes = []
            for _, grp in panel.groupby("iso3"):
                s = grp.sort_values("year")[ind].values
                changes.extend(np.diff(s[np.isfinite(s)]).tolist())
            if changes:
                ind_std[ind] = max(float(np.std(changes)), 0.01)
            else:
                ind_std[ind] = 0.1
        else:
            ind_std[ind] = 0.1

    # Get last year in panel to compute future year labels
    last_year = int(panel["year"].max())

    rows = []
    for iso3 in countries:
        state0 = last_obs.get(iso3, {})

        # Run n_draws Monte Carlo trajectories
        # draws shape: (n_draws, n_inds, horizon)
        ind_list = [ind for ind in process_order if ind in state0]
        if not ind_list:
            continue

        # Initialise draws: all start from last observed value
        n_inds = len(ind_list)
        ind_idx = {ind: i for i, ind in enumerate(ind_list)}

        # draws[draw, ind, step]: dim 0=samples, 1=indicators, 2=time
        draws = np.zeros((n_draws, n_inds, horizon + 1))
        for i, ind in enumerate(ind_list):
            draws[:, i, 0] = state0.get(ind, 0.0)

        for step in range(1, horizon + 1):
            for ind in process_order:
                if ind not in ind_idx:
                    continue
                i = ind_idx[ind]

                if ind in interventions:
                    # Clamped: linearly interpolated toward target
                    base_val = draws[:, i, 0]  # original last-observed value
                    clamped = _clamp_value(
                        base_val=draws[:, i, 0].mean(),  # use mean as anchor
                        magnitude=interventions[ind],
                        step=step,
                        horizon=horizon,
                        intervention_type=intervention_type,
                    )
                    # All draws get same clamped value (intervention is deterministic)
                    draws[:, i, step] = clamped
                else:
                    # Forward simulate from parents
                    parent_contribution = np.zeros(n_draws)
                    child_parents = dag.get(ind, [])
                    for parent, _source, _sign in child_parents:
                        if parent not in ind_idx:
                            continue
                        j = ind_idx[parent]
                        beta = coefs.get(ind, {}).get(parent, 0.0)
                        parent_contribution += beta * draws[:, j, step - 1]

                    sigma = ind_std.get(ind, 0.1)
                    noise = rng.normal(0, sigma, size=n_draws)
                    # New value = previous + causal update + noise
                    draws[:, i, step] = draws[:, i, step - 1] + parent_contribution + noise
                    # Clip to non-negative (most health indicators can't go below 0)
                    draws[:, i, step] = np.clip(draws[:, i, step], 0.0, None)

        # Summarise draws → mean + 80% CI
        for step in range(1, horizon + 1):
            year = last_year + step
            row: Dict = {"iso3": iso3, "year": year}
            for ind in ind_list:
                i = ind_idx[ind]
                vals = draws[:, i, step]
                row[f"{ind}_mean"] = float(np.mean(vals))
                row[f"{ind}_lo80"] = float(np.percentile(vals, 10))
                row[f"{ind}_hi80"] = float(np.percentile(vals, 90))
            rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def simulate_counterfactual(
    panel: pd.DataFrame,
    dag: dict,
    indicators: List[str],
    countries: List[str],
    intervention: Dict[str, float],
    intervention_type: str = "multiply",
    horizon: int = 15,
) -> CounterfactualResult:
    """
    Run do-operator counterfactual simulation.

    Runs _forward_simulate twice:
      1. Baseline: business-as-usual (no intervention)
      2. Counterfactual: with the specified intervention

    Finds affected indicators via 2-level get_children traversal.

    Parameters
    ----------
    panel           : pd.DataFrame — historical country-year panel
    dag             : {child: [(parent, source, sign), ...]}
    indicators      : list of indicator IDs to simulate
    countries       : list of ISO3 country codes
    intervention    : {indicator_id: magnitude}
    intervention_type : "multiply" or "add"
    horizon         : number of years to simulate

    Returns
    -------
    CounterfactualResult
    """
    rng = np.random.default_rng(SEED)

    baseline = _forward_simulate(
        panel=panel,
        dag=dag,
        indicators=indicators,
        countries=countries,
        horizon=horizon,
        interventions=None,
        intervention_type=intervention_type,
        n_draws=200,
        rng=rng,
    )

    # New rng with same seed for counterfactual (deterministic comparison)
    rng_cf = np.random.default_rng(SEED)

    counterfactual = _forward_simulate(
        panel=panel,
        dag=dag,
        indicators=indicators,
        countries=countries,
        horizon=horizon,
        interventions=intervention,
        intervention_type=intervention_type,
        n_draws=200,
        rng=rng_cf,
    )

    # Identify affected indicators: direct interventions + 2-level causal children
    affected: List[str] = list(intervention.keys())
    for ind in list(intervention.keys()):
        level1 = get_children(dag, ind)
        affected.extend(level1)
        for child1 in level1:
            affected.extend(get_children(dag, child1))

    # Deduplicate while preserving order
    seen: set = set()
    deduped: List[str] = []
    for x in affected:
        if x not in seen:
            seen.add(x)
            deduped.append(x)

    return CounterfactualResult(
        baseline=baseline,
        counterfactual=counterfactual,
        intervention=intervention,
        intervention_type=intervention_type,
        affected_indicators=deduped,
    )


def precompute_intervention_grid(
    panel: pd.DataFrame,
    dag: dict,
    indicators: List[str],
    countries: List[str],
    grid_spec: Dict[str, List[float]],
    horizon: int = 15,
) -> Dict[str, CounterfactualResult]:
    """
    Pre-compute counterfactuals for a grid of indicator × magnitude combinations.

    Parameters
    ----------
    panel      : historical panel
    dag        : causal DAG
    indicators : indicator IDs to simulate
    countries  : ISO3 country codes
    grid_spec  : {indicator_id: [magnitude1, magnitude2, ...]}
    horizon    : simulation horizon in years

    Returns
    -------
    dict: {"indicator_magnitude": CounterfactualResult}
        e.g. {"gdp_pc_1.5": result, "gdp_pc_2.0": result}
    """
    results: Dict[str, CounterfactualResult] = {}

    for indicator, magnitudes in grid_spec.items():
        for magnitude in magnitudes:
            key = f"{indicator}_{magnitude}"
            result = simulate_counterfactual(
                panel=panel,
                dag=dag,
                indicators=indicators,
                countries=countries,
                intervention={indicator: magnitude},
                intervention_type="multiply",
                horizon=horizon,
            )
            results[key] = result

    return results


def interpolate_intervention(
    grid: Dict[str, CounterfactualResult],
    indicator: str,
    magnitude: float,
    country: str,
) -> pd.DataFrame:
    """
    Linearly interpolate between two grid points to get counterfactual for a
    specific indicator magnitude not explicitly computed.

    Finds the two bracketing grid entries for `indicator` whose magnitudes
    straddle `magnitude`, then linearly interpolates column-wise.

    If `magnitude` exactly matches a grid point, returns that result directly.

    Parameters
    ----------
    grid      : output of precompute_intervention_grid
    indicator : which indicator was intervened on
    magnitude : the target magnitude to interpolate to
    country   : ISO3 country code to filter rows

    Returns
    -------
    pd.DataFrame with same columns as a single counterfactual DataFrame,
    filtered to the specified country.

    Raises
    ------
    ValueError : if fewer than 2 grid points exist for this indicator,
                 or magnitude is outside the grid range.
    """
    # Extract all grid points for this indicator
    prefix = f"{indicator}_"
    entries: List[tuple] = []  # (magnitude_float, CounterfactualResult)

    for key, result in grid.items():
        if key.startswith(prefix):
            suffix = key[len(prefix):]
            try:
                grid_mag = float(suffix)
            except ValueError:
                continue
            entries.append((grid_mag, result))

    if not entries:
        raise ValueError(f"No grid entries found for indicator '{indicator}'")

    # Sort by magnitude
    entries.sort(key=lambda t: t[0])

    # Check for exact match
    for grid_mag, result in entries:
        if abs(grid_mag - magnitude) < 1e-9:
            cf = result.counterfactual
            return cf[cf["iso3"] == country].reset_index(drop=True)

    if len(entries) < 2:
        raise ValueError(
            f"Need at least 2 grid points for interpolation; "
            f"found {len(entries)} for '{indicator}'"
        )

    mags = [e[0] for e in entries]
    if magnitude < mags[0] or magnitude > mags[-1]:
        raise ValueError(
            f"magnitude={magnitude} is outside grid range "
            f"[{mags[0]}, {mags[-1]}] for indicator '{indicator}'"
        )

    # Find bracketing pair
    lo_entry = entries[0]
    hi_entry = entries[-1]
    for i in range(len(entries) - 1):
        if entries[i][0] <= magnitude <= entries[i + 1][0]:
            lo_entry = entries[i]
            hi_entry = entries[i + 1]
            break

    lo_mag, lo_result = lo_entry
    hi_mag, hi_result = hi_entry

    lo_cf = lo_result.counterfactual
    hi_cf = hi_result.counterfactual

    lo_df = lo_cf[lo_cf["iso3"] == country].sort_values("year").reset_index(drop=True)
    hi_df = hi_cf[hi_cf["iso3"] == country].sort_values("year").reset_index(drop=True)

    if lo_df.empty or hi_df.empty:
        raise ValueError(f"No rows found for country '{country}'")

    # Interpolation weight
    span = hi_mag - lo_mag
    w = (magnitude - lo_mag) / span  # 0=lo, 1=hi

    # Linearly interpolate numeric columns
    result_df = lo_df.copy()
    numeric_cols = lo_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col == "year":
            continue
        result_df[col] = lo_df[col] + w * (hi_df[col] - lo_df[col])

    return result_df
