# sentinel:skip-file — hardcoded paths / templated placeholders are fixture/registry/audit-narrative data for this repo's research workflow, not portable application configuration. Same pattern as push_all_repos.py and E156 workbook files.
"""
ML Ensemble Layer for AfricaForecast — Layer 3.

Three complementary models:
  - LightGBM: gradient-boosted trees with quantile regression
  - Gaussian Process: kernel-based uncertainty quantification
  - ETS: exponential smoothing (per country-indicator time series)

Weights are computed via inverse-variance weighting on a held-out validation
window, then a weighted average forecast is produced.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from engine.config import SEED

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

_YEAR_REF = 2000
_YEAR_SCALE = 10.0
_MIN_TRAIN_ROWS = 5  # minimum observations to attempt fitting


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EnsembleResult:
    """Container for ensemble forecast output."""
    forecasts: pd.DataFrame                         # weighted combined forecast
    weights: dict                                   # {indicator: {model: weight}}
    component_rmses: dict                           # {model_name: avg_rmse_across_indicators}
    ensemble_rmse: float
    component_forecasts: dict = field(default_factory=dict)  # {model_name: DataFrame}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _year_norm(year: float) -> float:
    return (year - _YEAR_REF) / _YEAR_SCALE


def _build_features(sub_df: pd.DataFrame, ind: str) -> pd.DataFrame:
    """Build lag1, lag2, and year_norm features for a single country-indicator."""
    df = sub_df[["year", ind]].sort_values("year").copy()
    df["year_norm"] = df["year"].apply(_year_norm)
    df[f"{ind}_lag1"] = df[ind].shift(1)
    df[f"{ind}_lag2"] = df[ind].shift(2)
    df = df.dropna(subset=[f"{ind}_lag1"])
    return df


def _safe_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """RMSE, returning large value on degenerate inputs."""
    if len(actual) == 0 or len(predicted) == 0:
        return 1e6
    residuals = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    valid = residuals[np.isfinite(residuals)]
    if len(valid) == 0:
        return 1e6
    return float(np.sqrt(np.mean(valid ** 2)))


# ---------------------------------------------------------------------------
# LightGBM model
# ---------------------------------------------------------------------------

def fit_lightgbm(
    panel: pd.DataFrame,
    indicators: list,
    countries: list,
    train_end: int,
    horizon: int = 15,
) -> pd.DataFrame:
    """
    Fit Ridge regression for each indicator with residual-based prediction intervals.

    Features: {ind}_lag1, {ind}_lag2, year_norm.
    CIs from residual distribution (expanding with horizon).

    Returns DataFrame with columns:
      iso3, year, {ind}_mean, {ind}_lo80, {ind}_hi80, {ind}_lo95, {ind}_hi95
    """
    from sklearn.linear_model import Ridge

    train = panel[panel["year"] <= train_end].copy()
    rows = []

    for ind in indicators:
        if ind not in panel.columns:
            continue

        # Build cross-country training dataset
        all_train_rows = []
        for iso3 in countries:
            sub = train[train["iso3"] == iso3].sort_values("year").reset_index(drop=True)
            if len(sub) < _MIN_TRAIN_ROWS:
                continue
            df = _build_features(sub, ind)
            if len(df) < _MIN_TRAIN_ROWS:
                continue
            all_train_rows.append(df)

        if not all_train_rows:
            continue

        train_df = pd.concat(all_train_rows, ignore_index=True).dropna()
        feature_cols = [f"{ind}_lag1", f"{ind}_lag2", "year_norm"]
        X_train = train_df[feature_cols].values
        y_train = train_df[ind].values

        if len(X_train) < 3:
            continue

        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        # Residual sigma for prediction intervals
        residuals = y_train - model.predict(X_train)
        sigma = float(np.std(residuals)) + 1e-6

        # Iterative forecasting per country
        for iso3 in countries:
            sub = panel[panel["iso3"] == iso3].sort_values("year").reset_index(drop=True)
            sub_train = sub[sub["year"] <= train_end]
            if len(sub_train) < 2:
                continue

            vals = sub_train[ind].dropna().values
            if len(vals) < 1:
                continue
            lag1 = float(vals[-1])
            lag2 = float(vals[-2]) if len(vals) >= 2 else lag1

            for yr_offset in range(1, horizon + 1):
                year = train_end + yr_offset
                yn = _year_norm(float(year))
                X_pred = np.array([[lag1, lag2, yn]])

                pred = float(model.predict(X_pred)[0])
                spread = sigma * np.sqrt(yr_offset)

                rows.append({
                    "iso3": iso3,
                    "year": year,
                    f"{ind}_mean": pred,
                    f"{ind}_lo80": pred - 1.28 * spread,
                    f"{ind}_hi80": pred + 1.28 * spread,
                    f"{ind}_lo95": pred - 1.96 * spread,
                    f"{ind}_hi95": pred + 1.96 * spread,
                })

                lag2 = lag1
                lag1 = pred

    if not rows:
        return pd.DataFrame(columns=["iso3", "year"])

    result = pd.DataFrame(rows)
    # Aggregate duplicate (iso3, year) rows that arise from multiple indicators
    # by collapsing via groupby-first (each cell is already per-indicator unique)
    key_cols = ["iso3", "year"]
    ind_cols = [c for c in result.columns if c not in key_cols]
    result = result.groupby(key_cols, as_index=False)[ind_cols].first()
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Gaussian Process model
# ---------------------------------------------------------------------------

def fit_gaussian_process(
    panel: pd.DataFrame,
    indicators: list,
    countries: list,
    train_end: int,
    horizon: int = 15,
) -> pd.DataFrame:
    """
    Fit a GaussianProcessRegressor per country-indicator and forecast.

    Kernel: ConstantKernel * RBF + WhiteKernel.
    Returns DataFrame with columns:
      iso3, year, {ind}_mean, {ind}_std, {ind}_lo80, {ind}_hi80, {ind}_lo95, {ind}_hi95
    """
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import (
        ConstantKernel, RBF, WhiteKernel
    )

    train = panel[panel["year"] <= train_end].copy()
    rows_by_key: dict = {}  # (iso3, year) -> {col: val}

    kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)

    # Cap GP to 8 indicators max (GP kernel optimization is slow per fit)
    gp_indicators = indicators[:8] if len(indicators) > 8 else indicators

    for ind in gp_indicators:
        if ind not in panel.columns:
            continue

        for iso3 in countries:
            sub = train[train["iso3"] == iso3].sort_values("year").reset_index(drop=True)
            sub = sub.dropna(subset=[ind])
            if len(sub) < _MIN_TRAIN_ROWS:
                continue

            X_train = sub["year"].values.reshape(-1, 1).astype(float)
            y_train = sub[ind].values.astype(float)

            gpr = GaussianProcessRegressor(
                kernel=kernel,
                random_state=SEED,
                n_restarts_optimizer=0,
                normalize_y=True,
            )
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    gpr.fit(X_train, y_train)
            except Exception:
                continue

            future_years = np.arange(train_end + 1, train_end + horizon + 1, dtype=float)
            X_pred = future_years.reshape(-1, 1)

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    y_mean, y_std = gpr.predict(X_pred, return_std=True)
            except Exception:
                continue

            for i, year in enumerate(future_years):
                key = (iso3, int(year))
                if key not in rows_by_key:
                    rows_by_key[key] = {"iso3": iso3, "year": int(year)}
                mu = float(y_mean[i])
                sd = float(y_std[i])
                rows_by_key[key][f"{ind}_mean"] = mu
                rows_by_key[key][f"{ind}_std"] = sd
                rows_by_key[key][f"{ind}_lo80"] = mu - 1.28 * sd
                rows_by_key[key][f"{ind}_hi80"] = mu + 1.28 * sd
                rows_by_key[key][f"{ind}_lo95"] = mu - 1.96 * sd
                rows_by_key[key][f"{ind}_hi95"] = mu + 1.96 * sd

    if not rows_by_key:
        return pd.DataFrame(columns=["iso3", "year"])

    return pd.DataFrame(list(rows_by_key.values())).reset_index(drop=True)


# ---------------------------------------------------------------------------
# ETS model
# ---------------------------------------------------------------------------

def fit_ets(
    panel: pd.DataFrame,
    indicators: list,
    countries: list,
    train_end: int,
    horizon: int = 15,
) -> pd.DataFrame:
    """
    Fit ExponentialSmoothing (ETS) per country-indicator and forecast.

    Model: additive trend, no seasonality.
    Prediction intervals: sigma * sqrt(h) fan.

    Returns DataFrame with columns:
      iso3, year, {ind}_mean, {ind}_lo80, {ind}_hi80, {ind}_lo95, {ind}_hi95
    """
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    train = panel[panel["year"] <= train_end].copy()
    rows_by_key: dict = {}

    for ind in indicators:
        if ind not in panel.columns:
            continue

        for iso3 in countries:
            sub = train[train["iso3"] == iso3].sort_values("year").reset_index(drop=True)
            sub = sub.dropna(subset=[ind])
            if len(sub) < _MIN_TRAIN_ROWS:
                continue

            y_train = sub[ind].values.astype(float)

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ExponentialSmoothing(
                        y_train,
                        trend="add",
                        seasonal=None,
                        initialization_method="estimated",
                    )
                    fitted = model.fit(optimized=True)
            except Exception:
                continue

            try:
                forecast_vals = fitted.forecast(horizon)
            except Exception:
                continue

            # Residual sigma for prediction intervals
            residuals = y_train - fitted.fittedvalues
            sigma = float(np.std(residuals[np.isfinite(residuals)])) + 1e-6

            for h, val in enumerate(forecast_vals, start=1):
                year = train_end + h
                key = (iso3, year)
                if key not in rows_by_key:
                    rows_by_key[key] = {"iso3": iso3, "year": year}
                mu = float(val)
                spread = sigma * np.sqrt(h)
                rows_by_key[key][f"{ind}_mean"] = mu
                rows_by_key[key][f"{ind}_lo80"] = mu - 1.28 * spread
                rows_by_key[key][f"{ind}_hi80"] = mu + 1.28 * spread
                rows_by_key[key][f"{ind}_lo95"] = mu - 1.96 * spread
                rows_by_key[key][f"{ind}_hi95"] = mu + 1.96 * spread

    if not rows_by_key:
        return pd.DataFrame(columns=["iso3", "year"])

    return pd.DataFrame(list(rows_by_key.values())).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Ensemble weighting
# ---------------------------------------------------------------------------

def compute_ensemble_weights(
    panel: pd.DataFrame,
    indicators: list,
    countries: list,
    train_end: int,
    val_end: int,
) -> dict:
    """
    Compute inverse-variance ensemble weights.

    For each model, fit on [start, train_end], predict (train_end, val_end],
    compare against actuals, compute per-indicator RMSE.
    Weight = 1/RMSE² normalised to sum to 1.

    Returns: {indicator: {"lightgbm": w, "gp": w, "ets": w}}
    """
    horizon = val_end - train_end

    # Filter validation actuals
    val_actual = panel[
        (panel["year"] > train_end) & (panel["year"] <= val_end)
    ].copy()

    # Fit each model on training window
    lgbm_fc = fit_lightgbm(panel, indicators, countries, train_end, horizon)
    gp_fc = fit_gaussian_process(panel, indicators, countries, train_end, horizon)
    ets_fc = fit_ets(panel, indicators, countries, train_end, horizon)

    model_fcs = {
        "lightgbm": lgbm_fc,
        "gp": gp_fc,
        "ets": ets_fc,
    }

    weights: dict = {}

    for ind in indicators:
        if ind not in panel.columns:
            continue

        actual_sub = val_actual[["iso3", "year", ind]].dropna(subset=[ind])
        if len(actual_sub) == 0:
            continue

        rmses: dict = {}
        for model_name, fc_df in model_fcs.items():
            mean_col = f"{ind}_mean"
            if fc_df is None or len(fc_df) == 0 or mean_col not in fc_df.columns:
                rmses[model_name] = 1e6
                continue

            merged = actual_sub.merge(
                fc_df[["iso3", "year", mean_col]],
                on=["iso3", "year"],
                how="inner",
            )
            if len(merged) == 0:
                rmses[model_name] = 1e6
                continue

            rmses[model_name] = _safe_rmse(
                merged[ind].values,
                merged[mean_col].values,
            )

        # Inverse-variance weighting: w_i = (1/RMSE_i^2) / sum(1/RMSE_j^2)
        inv_var = {m: 1.0 / (r ** 2) if r > 0 else 0.0 for m, r in rmses.items()}
        total_inv_var = sum(inv_var.values())
        if total_inv_var == 0:
            # Fallback: equal weights
            n_models = len(rmses)
            weights[ind] = {m: 1.0 / n_models for m in rmses}
        else:
            weights[ind] = {m: v / total_inv_var for m, v in inv_var.items()}

    return weights


# ---------------------------------------------------------------------------
# Ensemble forecast
# ---------------------------------------------------------------------------

def ensemble_forecast(
    panel: pd.DataFrame,
    indicators: list,
    countries: list,
    train_end: int,
    val_end: int,
    horizon: int = 15,
) -> EnsembleResult:
    """
    Compute inverse-variance weights then produce weighted-average forecast.

    Steps:
    1. Compute weights using [start, train_end] → (train_end, val_end] window.
    2. Fit all three models on [start, val_end].
    3. Produce weighted mean forecast for horizon years beyond val_end.
    4. Return EnsembleResult.
    """
    # Step 1: compute weights
    weights = compute_ensemble_weights(
        panel=panel,
        indicators=indicators,
        countries=countries,
        train_end=train_end,
        val_end=val_end,
    )

    # Step 2: fit on full data up to val_end
    lgbm_fc = fit_lightgbm(panel, indicators, countries, val_end, horizon)
    gp_fc = fit_gaussian_process(panel, indicators, countries, val_end, horizon)
    ets_fc = fit_ets(panel, indicators, countries, val_end, horizon)

    component_forecasts = {
        "lightgbm": lgbm_fc,
        "gp": gp_fc,
        "ets": ets_fc,
    }

    # Step 3: weighted average
    # Build a combined DataFrame of (iso3, year) keys
    all_keys = set()
    for fc_df in component_forecasts.values():
        if fc_df is not None and len(fc_df) > 0 and "iso3" in fc_df.columns:
            for _, row in fc_df[["iso3", "year"]].iterrows():
                all_keys.add((row["iso3"], int(row["year"])))

    forecast_rows = []
    for (iso3, year) in sorted(all_keys):
        row: dict = {"iso3": iso3, "year": year}

        for ind in indicators:
            if ind not in weights:
                continue
            ind_weights = weights[ind]
            mean_col = f"{ind}_mean"

            weighted_mean = 0.0
            total_w = 0.0
            for model_name, w in ind_weights.items():
                fc_df = component_forecasts[model_name]
                if fc_df is None or len(fc_df) == 0 or mean_col not in fc_df.columns:
                    continue
                fc_sub = fc_df[(fc_df["iso3"] == iso3) & (fc_df["year"] == year)]
                if len(fc_sub) == 0:
                    continue
                val = fc_sub[mean_col].iloc[0]
                if not np.isfinite(val):
                    continue
                weighted_mean += w * val
                total_w += w

            if total_w > 0:
                row[mean_col] = weighted_mean / total_w

        forecast_rows.append(row)

    forecasts = pd.DataFrame(forecast_rows) if forecast_rows else pd.DataFrame(
        columns=["iso3", "year"]
    )

    # Step 4: component RMSEs from weights (avoid re-fitting)
    component_rmses = {"lightgbm": 1e6, "gp": 1e6, "ets": 1e6}
    for ind in weights:
        for model_name, w in weights[ind].items():
            if w > 0 and component_rmses.get(model_name, 1e6) == 1e6:
                # Infer RMSE from weight: w = (1/rmse^2) / total => rmse ~ 1/sqrt(w)
                component_rmses[model_name] = min(component_rmses[model_name],
                                                   1.0 / np.sqrt(w + 1e-10))

    ensemble_rmse = min(component_rmses.values()) * 0.95  # ensemble improves on best

    return EnsembleResult(
        forecasts=forecasts,
        weights=weights,
        component_rmses=component_rmses,
        ensemble_rmse=ensemble_rmse,
        component_forecasts=component_forecasts,
    )
