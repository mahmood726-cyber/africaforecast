"""
Tests for the ML Ensemble: LightGBM + Gaussian Process + ETS + inverse-variance weighting.
"""

import numpy as np
import pandas as pd
import pytest

from engine.ensemble import (
    fit_lightgbm,
    fit_gaussian_process,
    fit_ets,
    compute_ensemble_weights,
    ensemble_forecast,
    EnsembleResult,
)


class TestIndividualModels:
    """Tests for each individual model component."""

    def test_lightgbm_returns_predictions(
        self, synthetic_panel, mini_indicators, mini_country_list
    ):
        """fit_lightgbm must return a DataFrame with iso3/year columns and len > 0."""
        result_df = fit_lightgbm(
            panel=synthetic_panel,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2015,
            horizon=5,
        )
        assert isinstance(result_df, pd.DataFrame), "fit_lightgbm must return a DataFrame"
        assert len(result_df) > 0, "fit_lightgbm must return non-empty DataFrame"
        assert "iso3" in result_df.columns, "Missing 'iso3' column"
        assert "year" in result_df.columns, "Missing 'year' column"

    def test_gp_returns_predictions_with_uncertainty(
        self, synthetic_panel, mini_indicators, mini_country_list
    ):
        """fit_gaussian_process must return _mean and _std columns per indicator."""
        result_df = fit_gaussian_process(
            panel=synthetic_panel,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2015,
            horizon=5,
        )
        assert isinstance(result_df, pd.DataFrame), "fit_gaussian_process must return a DataFrame"
        assert len(result_df) > 0, "fit_gaussian_process must return non-empty DataFrame"
        assert "iso3" in result_df.columns, "Missing 'iso3' column"
        assert "year" in result_df.columns, "Missing 'year' column"

        # Check that _mean and _std columns exist for each indicator
        for ind in mini_indicators:
            mean_col = f"{ind}_mean"
            std_col = f"{ind}_std"
            assert mean_col in result_df.columns, (
                f"Missing '{mean_col}' column in GP result"
            )
            assert std_col in result_df.columns, (
                f"Missing '{std_col}' column in GP result"
            )

    def test_ets_returns_predictions(
        self, synthetic_panel, mini_indicators, mini_country_list
    ):
        """fit_ets must return a DataFrame with len > 0."""
        result_df = fit_ets(
            panel=synthetic_panel,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2015,
            horizon=5,
        )
        assert isinstance(result_df, pd.DataFrame), "fit_ets must return a DataFrame"
        assert len(result_df) > 0, "fit_ets must return non-empty DataFrame"
        assert "iso3" in result_df.columns, "Missing 'iso3' column"
        assert "year" in result_df.columns, "Missing 'year' column"


class TestEnsemble:
    """Tests for ensemble weighting and combined forecast."""

    def test_weights_sum_to_one(
        self, synthetic_panel, mini_indicators, mini_country_list
    ):
        """compute_ensemble_weights must return weights that sum to ~1.0 per indicator."""
        weights = compute_ensemble_weights(
            panel=synthetic_panel,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2012,
            val_end=2015,
        )
        assert isinstance(weights, dict), "compute_ensemble_weights must return a dict"
        assert len(weights) > 0, "Weights dict must not be empty"

        for ind, model_weights in weights.items():
            total = sum(model_weights.values())
            assert abs(total - 1.0) < 1e-6, (
                f"Weights for indicator '{ind}' sum to {total:.6f}, expected 1.0"
            )

    def test_ensemble_forecast_shape(
        self, synthetic_panel, mini_indicators, mini_country_list
    ):
        """ensemble_forecast must return an EnsembleResult with non-empty forecasts containing iso3/year."""
        result = ensemble_forecast(
            panel=synthetic_panel,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2012,
            val_end=2015,
            horizon=5,
        )
        assert isinstance(result, EnsembleResult), (
            "ensemble_forecast must return an EnsembleResult"
        )
        assert isinstance(result.forecasts, pd.DataFrame), (
            "EnsembleResult.forecasts must be a DataFrame"
        )
        assert len(result.forecasts) > 0, (
            "EnsembleResult.forecasts must be non-empty"
        )
        assert "iso3" in result.forecasts.columns, (
            "Missing 'iso3' column in ensemble forecasts"
        )
        assert "year" in result.forecasts.columns, (
            "Missing 'year' column in ensemble forecasts"
        )
