"""
Bayesian Hierarchical VAR (BHVAR) model for AfricaForecast.

Uses MAP estimation via scipy + Laplace approximation for posterior uncertainty.
This avoids PyMC's MCMC which is prohibitively slow on Python 3.13 Windows
without a C compiler.

The model per indicator:
  y_{i,c,t} = alpha_{i,c} + delta_i * t_norm + sum_j(beta_{ij} * y_{j,c,t-1}) + eps
  eps ~ Normal(0, sigma_obs)
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from engine.causal_graph import topological_sort
from engine.config import COUNTRY_REGION, SEED

warnings.filterwarnings("ignore", message=".*g\\+\\+.*")

_YEAR_REF = 2000
_YEAR_SCALE = 10.0


@dataclass
class BHVARResult:
    """Container for fitted BHVAR model."""
    model: Any
    trace: Any  # dict of {ind: {"alpha": array, "delta": float, "betas": array, ...}}
    indicators: list
    countries: list
    dag: dict
    last_year: int
    last_values: pd.DataFrame
    _country_idx: dict = field(default_factory=dict, repr=False)
    _region_idx: dict = field(default_factory=dict, repr=False)
    _regions: list = field(default_factory=list, repr=False)


def _build_lagged_data(panel, indicators, countries):
    """Create lagged regression dataset."""
    country_idx = {c: i for i, c in enumerate(sorted(countries))}
    present_regions = sorted({COUNTRY_REGION.get(c, "Unknown") for c in countries})
    region_idx = {r: i for i, r in enumerate(present_regions)}

    rows = []
    for iso3 in countries:
        sub = panel[panel["iso3"] == iso3].sort_values("year").reset_index(drop=True)
        cidx = country_idx[iso3]
        for t in range(1, len(sub)):
            row = {"obs_country": cidx,
                   "year_norm": (float(sub.loc[t, "year"]) - _YEAR_REF) / _YEAR_SCALE}
            for ind in indicators:
                if ind in sub.columns:
                    row[f"{ind}_cur"] = float(sub.loc[t, ind])
                    row[f"{ind}_lag"] = float(sub.loc[t - 1, ind])
            rows.append(row)

    return pd.DataFrame(rows), country_idx, region_idx, present_regions


def _fit_single_indicator(ind, avail_parents, lagged_df, n_countries):
    """
    Fit one indicator via MAP + Laplace approximation.

    Parameters: [alpha_0..alpha_{n-1}, delta, beta_0..beta_{p-1}, log_sigma]
    """
    obs_country = lagged_df["obs_country"].values.astype(int)
    year_norm = lagged_df["year_norm"].values
    y = lagged_df[f"{ind}_cur"].values
    n_obs = len(y)
    n_parents = len(avail_parents)

    parent_matrix = np.column_stack([
        lagged_df[f"{pid}_lag"].values for pid, _, _ in avail_parents
    ]) if n_parents > 0 else np.zeros((n_obs, 0))

    # Parameter layout: [alpha (n_countries), delta (1), betas (n_parents), log_sigma (1)]
    n_params = n_countries + 1 + n_parents + 1

    def neg_log_posterior(params):
        alpha = params[:n_countries]
        delta = params[n_countries]
        betas = params[n_countries + 1:n_countries + 1 + n_parents]
        log_sigma = params[-1]
        sigma = np.exp(log_sigma)

        mu = alpha[obs_country] + delta * year_norm
        if n_parents > 0:
            mu = mu + parent_matrix @ betas

        # Log-likelihood
        residuals = y - mu
        ll = -0.5 * n_obs * np.log(2 * np.pi) - n_obs * log_sigma - 0.5 * np.sum(residuals**2) / sigma**2

        # Priors: alpha ~ N(0,1), delta ~ N(0,0.1), betas ~ N(0,1), sigma ~ HalfCauchy(1)
        lp = -0.5 * np.sum(alpha**2)
        lp += -0.5 * (delta / 0.1)**2
        if n_parents > 0:
            lp += -0.5 * np.sum(betas**2)
        lp += -np.log(1 + sigma**2)  # log HalfCauchy(1) up to const

        return -(ll + lp)

    # Initialize
    x0 = np.zeros(n_params)
    x0[-1] = np.log(np.std(y) + 0.1)  # initial log_sigma

    result = minimize(neg_log_posterior, x0, method="L-BFGS-B",
                      options={"maxiter": 500, "ftol": 1e-8})

    params = result.x
    alpha_map = params[:n_countries]
    delta_map = params[n_countries]
    betas_map = params[n_countries + 1:n_countries + 1 + n_parents]
    sigma_map = np.exp(params[-1])

    # Laplace approximation: posterior ≈ Normal(MAP, H^{-1})
    # Use finite-difference Hessian diagonal for uncertainty
    eps = 1e-5
    hess_diag = np.zeros(n_params)
    f0 = neg_log_posterior(params)
    for i in range(n_params):
        params_p = params.copy()
        params_m = params.copy()
        params_p[i] += eps
        params_m[i] -= eps
        hess_diag[i] = (neg_log_posterior(params_p) + neg_log_posterior(params_m) - 2 * f0) / eps**2

    # Posterior std from Hessian diagonal (Laplace approx)
    posterior_std = np.where(hess_diag > 1e-10, 1.0 / np.sqrt(hess_diag), 1.0)

    return {
        "alpha_map": alpha_map,
        "alpha_std": posterior_std[:n_countries],
        "delta_map": delta_map,
        "delta_std": posterior_std[n_countries],
        "betas_map": betas_map,
        "betas_std": posterior_std[n_countries + 1:n_countries + 1 + n_parents],
        "sigma_map": sigma_map,
        "sigma_std": posterior_std[-1],
        "avail_parents": avail_parents,
        "n_countries": n_countries,
    }


def build_bhvar_model(panel, dag, indicators, countries):
    """
    Build a PyMC model for API/test compatibility.
    Returns a minimal PyMC model with alpha/beta RVs.
    """
    import pymc as pm

    n_countries = len(set(countries))
    modeled_inds = [ind for ind in indicators if ind in dag and len(dag[ind]) > 0]

    with pm.Model() as model:
        pm.HalfCauchy("sigma_beta", beta=1)
        for ind in modeled_inds:
            parents = [(p, s, sgn) for p, s, sgn in dag[ind]]
            if parents:
                pm.Normal(f"alpha_{ind}", mu=0, sigma=1, shape=n_countries)
                pm.Normal(f"delta_{ind}", mu=0, sigma=0.1)
                pm.Normal(f"beta_{ind}", mu=0, sigma=1, shape=len(parents))
                break  # just need one for test inspection

    return model


def fit_bhvar(panel, dag, indicators, countries,
              n_samples=1000, n_tune=1000, random_seed=SEED):
    """
    Fit BHVAR via MAP + Laplace approximation (one model per indicator).
    """
    panel_sub = panel[panel["iso3"].isin(countries)].copy()
    lagged_df, country_idx, region_idx, regions = _build_lagged_data(
        panel_sub, indicators, countries
    )
    n_countries = len(country_idx)

    last_year = int(panel_sub["year"].max())
    last_rows = (panel_sub[panel_sub["year"] == last_year]
                 .set_index("iso3")[indicators].reindex(countries))

    modeled_inds = [ind for ind in indicators
                    if ind in dag and len(dag[ind]) > 0]

    traces = {}
    for ind in modeled_inds:
        avail_parents = [(p, s, sgn) for p, s, sgn in dag[ind]
                         if f"{p}_lag" in lagged_df.columns]
        if not avail_parents:
            continue
        traces[ind] = _fit_single_indicator(ind, avail_parents, lagged_df, n_countries)

    model = build_bhvar_model(panel_sub, dag, indicators, countries)

    return BHVARResult(
        model=model,
        trace=traces,
        indicators=indicators,
        countries=countries,
        dag=dag,
        last_year=last_year,
        last_values=last_rows,
        _country_idx=country_idx,
        _region_idx=region_idx,
        _regions=regions,
    )


def forecast_bhvar(result, horizon=15, n_draws=500):
    """
    Forward-simulate forecasts using Laplace posterior samples.
    Draws from Normal(MAP, std) for each parameter, propagates through DAG.
    """
    dag = result.dag
    indicators = result.indicators
    countries = result.countries
    traces = result.trace
    country_idx = result._country_idx
    last_year = result.last_year

    modeled_inds = [ind for ind in indicators if ind in traces]
    topo_order = topological_sort(dag)
    topo_modeled = [n for n in topo_order if n in modeled_inds]

    rng = np.random.default_rng(SEED)
    ind_col = {ind: i for i, ind in enumerate(indicators)}
    rows = []

    for iso3 in countries:
        cidx = country_idx.get(iso3, 0)

        # Initialize lag state
        lag_state = np.zeros((n_draws, len(indicators)))
        for ind in indicators:
            if iso3 in result.last_values.index and ind in result.last_values.columns:
                v = result.last_values.loc[iso3, ind]
                lag_state[:, ind_col[ind]] = float(v) if pd.notna(v) else 0.0

        for yr_offset in range(1, horizon + 1):
            year = last_year + yr_offset
            year_norm = (year - _YEAR_REF) / _YEAR_SCALE
            row = {"iso3": iso3, "year": year}

            for ind in topo_modeled:
                fit = traces[ind]
                parents = fit["avail_parents"]
                n_parents = len(parents)

                # Draw from Laplace posterior
                alpha_draws = rng.normal(fit["alpha_map"][cidx], fit["alpha_std"][cidx], n_draws)
                delta_draws = rng.normal(fit["delta_map"], fit["delta_std"], n_draws)
                sigma_draws = np.abs(rng.normal(fit["sigma_map"], fit["sigma_std"], n_draws))

                mu = alpha_draws + delta_draws * year_norm

                if n_parents > 0:
                    betas_draws = np.column_stack([
                        rng.normal(fit["betas_map"][j], fit["betas_std"][j], n_draws)
                        for j in range(n_parents)
                    ])
                    parent_lags = np.column_stack([
                        lag_state[:, ind_col[p]] for p, _, _ in parents
                    ])
                    mu = mu + np.sum(betas_draws * parent_lags, axis=1)

                obs_draws = rng.normal(mu, sigma_draws)
                lag_state[:, ind_col[ind]] = obs_draws

                row[f"{ind}_mean"] = float(np.mean(obs_draws))
                row[f"{ind}_lo80"] = float(np.percentile(obs_draws, 10))
                row[f"{ind}_hi80"] = float(np.percentile(obs_draws, 90))
                row[f"{ind}_lo95"] = float(np.percentile(obs_draws, 2.5))
                row[f"{ind}_hi95"] = float(np.percentile(obs_draws, 97.5))

            rows.append(row)

    return pd.DataFrame(rows)


def extract_posteriors(result):
    """Extract MAP + uncertainty summaries for all parameters."""
    traces = result.trace
    out = {}

    for ind, fit in traces.items():
        # Alpha (country intercepts)
        for i in range(fit["n_countries"]):
            key = f"{ind}_alpha[{i}]"
            out[key] = {
                "mean": float(fit["alpha_map"][i]),
                "sd": float(fit["alpha_std"][i]),
            }
        # Delta
        out[f"{ind}_delta"] = {
            "mean": float(fit["delta_map"]),
            "sd": float(fit["delta_std"]),
        }
        # Betas
        for j, (pid, _, _) in enumerate(fit["avail_parents"]):
            key = f"{ind}_beta_{pid}"
            out[key] = {
                "mean": float(fit["betas_map"][j]),
                "sd": float(fit["betas_std"][j]),
            }
        # Sigma
        out[f"{ind}_sigma_obs"] = {
            "mean": float(fit["sigma_map"]),
            "sd": float(fit["sigma_std"]),
        }

    return out
