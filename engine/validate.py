"""
Validation Module for AfricaForecast — Layer 4.

Measures forecast quality via:
  - RMSE and MAE point accuracy
  - Coverage calibration (80% and 95% prediction intervals)
  - Naive (linear extrapolation) benchmark comparison
  - Full holdout validation pipeline against ensemble forecasts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from engine.config import TRAIN_END, VALIDATE_END
from engine.ensemble import ensemble_forecast


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class IndicatorMetrics:
    """Per-indicator validation metrics."""
    indicator: str
    rmse: float
    mae: float
    coverage_80: float
    coverage_95: float
    naive_rmse: float
    improvement_pct: float


@dataclass
class ValidationReport:
    """Aggregate validation report across all indicators."""
    per_indicator: list[IndicatorMetrics]
    overall_rmse: float
    overall_mae: float
    mean_coverage_80: float
    mean_coverage_95: float
    mean_improvement_pct: float
    countries_modeled: int
    indicators_validated: int


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def compute_rmse(
    actual: Sequence[float],
    predicted: Sequence[float],
) -> float:
    """Root mean squared error between actual and predicted values."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.sqrt(np.mean((a - p) ** 2)))


def compute_mae(
    actual: Sequence[float],
    predicted: Sequence[float],
) -> float:
    """Mean absolute error between actual and predicted values."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.mean(np.abs(a - p)))


def compute_coverage(
    actual: Sequence[float],
    lo: Sequence[float],
    hi: Sequence[float],
) -> float:
    """
    Fraction of actual values that lie within the [lo, hi] interval.

    Returns a value in [0.0, 1.0].
    """
    a = np.asarray(actual, dtype=float)
    l = np.asarray(lo, dtype=float)
    h = np.asarray(hi, dtype=float)
    if len(a) == 0:
        return 0.0
    covered = np.sum((a >= l) & (a <= h))
    return float(covered / len(a))


def compute_calibration(
    actual: Sequence[float],
    lo80: Sequence[float],
    hi80: Sequence[float],
    lo95: Sequence[float],
    hi95: Sequence[float],
) -> dict:
    """
    Compute empirical coverage for 80% and 95% prediction intervals.

    Returns:
        {"coverage_80": float, "coverage_95": float}
    """
    return {
        "coverage_80": compute_coverage(actual, lo80, hi80),
        "coverage_95": compute_coverage(actual, lo95, hi95),
    }


def benchmark_vs_naive(
    actual: Sequence[float],
    model_pred: Sequence[float],
    naive_pred: Sequence[float],
) -> dict:
    """
    Compare model forecast against a naive baseline.

    Returns:
        {
            "model_rmse": float,
            "naive_rmse": float,
            "improvement_pct": float,   # positive = model better than naive
        }
    """
    model_rmse = compute_rmse(actual, model_pred)
    naive_rmse = compute_rmse(actual, naive_pred)

    if naive_rmse > 0:
        improvement_pct = float((naive_rmse - model_rmse) / naive_rmse * 100.0)
    else:
        improvement_pct = 0.0

    return {
        "model_rmse": model_rmse,
        "naive_rmse": naive_rmse,
        "improvement_pct": improvement_pct,
    }


# ---------------------------------------------------------------------------
# Naive forecast (linear extrapolation from last 10 training years)
# ---------------------------------------------------------------------------

def _naive_forecast(
    panel: pd.DataFrame,
    indicator: str,
    countries: list,
    train_end: int,
    val_end: int,
) -> pd.DataFrame:
    """
    Naive forecast: fit a linear trend to the last 10 training years per
    country-indicator, then extrapolate into (train_end, val_end].

    Returns DataFrame with columns: iso3, year, {indicator}_naive.
    """
    rows = []
    horizon = val_end - train_end
    train_df = panel[panel["year"] <= train_end].copy()

    for iso3 in countries:
        sub = (
            train_df[train_df["iso3"] == iso3]
            .sort_values("year")
            .dropna(subset=[indicator])
        )
        if len(sub) == 0:
            continue

        # Use last 10 years of training data
        sub = sub.tail(10)

        years = sub["year"].values.astype(float)
        vals = sub[indicator].values.astype(float)

        if len(years) < 2:
            # Flat extrapolation with single point
            slope = 0.0
            intercept = vals[-1]
        else:
            # Fit line: y = slope * year + intercept
            coeffs = np.polyfit(years, vals, deg=1)
            slope = float(coeffs[0])
            intercept = float(coeffs[1])

        for h in range(1, horizon + 1):
            year = train_end + h
            naive_val = slope * year + intercept
            rows.append({
                "iso3": iso3,
                "year": year,
                f"{indicator}_naive": float(naive_val),
            })

    if not rows:
        return pd.DataFrame(columns=["iso3", "year", f"{indicator}_naive"])

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Holdout validation pipeline
# ---------------------------------------------------------------------------

def run_holdout_validation(
    panel: pd.DataFrame,
    dag: dict,
    indicators: list,
    countries: list,
    train_end: int = TRAIN_END,
    val_end: int = VALIDATE_END,
) -> ValidationReport:
    """
    Run holdout validation by:
    1. Calling ensemble_forecast with train window [start, train_end].
    2. Comparing forecasts against actuals in (train_end, val_end].
    3. Computing RMSE, MAE, coverage, and naive benchmark for each indicator.
    4. Returning an aggregated ValidationReport.

    Parameters
    ----------
    panel       : country-year panel DataFrame
    dag         : causal DAG (passed for context; not used directly in validation)
    indicators  : list of indicator IDs to validate
    countries   : list of ISO3 country codes
    train_end   : last year of training window
    val_end     : last year of validation window
    """
    # Step 1: run ensemble on the train window, forecasting into val window.
    # ensemble_forecast needs train_end < val_end to compute weights.
    # We use an internal 3-year pre-split for weight learning, then fit up to
    # train_end and forecast val_horizon steps into (train_end, val_end].
    val_horizon = val_end - train_end
    internal_train = max(train_end - 3, panel["year"].min() + 5)
    ens_result = ensemble_forecast(
        panel=panel,
        indicators=indicators,
        countries=countries,
        train_end=internal_train,
        val_end=train_end,   # weight computation window
        horizon=val_horizon,  # forecast (train_end, train_end+val_horizon] = (train_end, val_end]
    )

    forecasts = ens_result.forecasts  # columns: iso3, year, {ind}_mean, ...

    # Step 2: actual validation data
    actuals = panel[
        (panel["year"] > train_end) & (panel["year"] <= val_end)
    ].copy()

    per_indicator: list[IndicatorMetrics] = []
    countries_with_data: set = set()

    for ind in indicators:
        mean_col = f"{ind}_mean"
        lo80_col = f"{ind}_lo80"
        hi80_col = f"{ind}_hi80"
        lo95_col = f"{ind}_lo95"
        hi95_col = f"{ind}_hi95"

        # Skip if indicator not in actuals
        if ind not in actuals.columns:
            continue

        actual_sub = actuals[["iso3", "year", ind]].dropna(subset=[ind])
        if len(actual_sub) == 0:
            continue

        # Check that mean forecasts exist
        if mean_col not in forecasts.columns:
            continue

        # Determine which CI columns are available
        has_ci = (
            lo80_col in forecasts.columns
            and hi80_col in forecasts.columns
            and lo95_col in forecasts.columns
            and hi95_col in forecasts.columns
        )

        # Build merge columns
        fc_cols = ["iso3", "year", mean_col]
        if has_ci:
            fc_cols += [lo80_col, hi80_col, lo95_col, hi95_col]

        merged = actual_sub.merge(
            forecasts[fc_cols],
            on=["iso3", "year"],
            how="inner",
        )

        if len(merged) == 0:
            continue

        a_vals = merged[ind].values
        p_vals = merged[mean_col].values

        # Track which countries contributed
        countries_with_data.update(merged["iso3"].unique())

        # RMSE and MAE
        rmse = compute_rmse(a_vals, p_vals)
        mae = compute_mae(a_vals, p_vals)

        # Coverage (use zeros if CI columns not available)
        if has_ci:
            cov80 = compute_coverage(a_vals, merged[lo80_col].values, merged[hi80_col].values)
            cov95 = compute_coverage(a_vals, merged[lo95_col].values, merged[hi95_col].values)
        else:
            cov80 = 0.0
            cov95 = 0.0

        # Naive benchmark
        naive_df = _naive_forecast(panel, ind, countries, train_end, val_end)
        naive_col = f"{ind}_naive"

        if len(naive_df) > 0 and naive_col in naive_df.columns:
            naive_merged = actual_sub.merge(
                naive_df[["iso3", "year", naive_col]],
                on=["iso3", "year"],
                how="inner",
            )
            if len(naive_merged) > 0:
                naive_rmse = compute_rmse(
                    naive_merged[ind].values,
                    naive_merged[naive_col].values,
                )
            else:
                naive_rmse = float("nan")
        else:
            naive_rmse = float("nan")

        if np.isfinite(naive_rmse) and naive_rmse > 0:
            improvement_pct = (naive_rmse - rmse) / naive_rmse * 100.0
        else:
            improvement_pct = 0.0

        per_indicator.append(IndicatorMetrics(
            indicator=ind,
            rmse=rmse,
            mae=mae,
            coverage_80=cov80,
            coverage_95=cov95,
            naive_rmse=naive_rmse if np.isfinite(naive_rmse) else 0.0,
            improvement_pct=float(improvement_pct),
        ))

    # Step 3: aggregate
    n = len(per_indicator)
    if n == 0:
        return ValidationReport(
            per_indicator=[],
            overall_rmse=0.0,
            overall_mae=0.0,
            mean_coverage_80=0.0,
            mean_coverage_95=0.0,
            mean_improvement_pct=0.0,
            countries_modeled=0,
            indicators_validated=0,
        )

    overall_rmse = float(np.mean([m.rmse for m in per_indicator]))
    overall_mae = float(np.mean([m.mae for m in per_indicator]))
    mean_cov80 = float(np.mean([m.coverage_80 for m in per_indicator]))
    mean_cov95 = float(np.mean([m.coverage_95 for m in per_indicator]))
    mean_imp = float(np.mean([m.improvement_pct for m in per_indicator]))

    return ValidationReport(
        per_indicator=per_indicator,
        overall_rmse=overall_rmse,
        overall_mae=overall_mae,
        mean_coverage_80=mean_cov80,
        mean_coverage_95=mean_cov95,
        mean_improvement_pct=mean_imp,
        countries_modeled=len(countries_with_data),
        indicators_validated=n,
    )
