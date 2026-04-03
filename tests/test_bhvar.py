"""
Tests for the Bayesian Hierarchical VAR (BHVAR) model.

Tests are intentionally fast: n_samples=50, n_tune=50, cores=1.
PyTensor g++ warnings are expected and harmless on this machine.
"""

import numpy as np
import pytest

from engine.bhvar import (
    BHVARResult,
    build_bhvar_model,
    fit_bhvar,
    forecast_bhvar,
    extract_posteriors,
)


class TestBHVARModel:
    """Tests for model construction, fitting, forecasting, and uncertainty."""

    def test_build_model_returns_pymc_model(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """build_bhvar_model must return a non-None PyMC model
        containing 'beta' and 'alpha' among its free RV names."""
        import pymc as pm

        model = build_bhvar_model(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
        )
        assert model is not None
        assert isinstance(model, pm.Model)

        # Collect all free RV names (may include trailing _log__ etc.)
        rv_names = [rv.name for rv in model.free_RVs]
        # At least one name must start with "beta" and at least one with "alpha"
        has_beta = any("beta" in name for name in rv_names)
        has_alpha = any("alpha" in name for name in rv_names)
        assert has_beta, f"No 'beta' RV found in model. RVs: {rv_names}"
        assert has_alpha, f"No 'alpha' RV found in model. RVs: {rv_names}"

    def test_fit_returns_result(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """fit_bhvar must return a BHVARResult with trace and model set."""
        result = fit_bhvar(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            n_samples=50,
            n_tune=50,
        )
        assert isinstance(result, BHVARResult)
        assert result.model is not None
        assert result.trace is not None
        assert result.indicators == mini_indicators
        assert result.countries == mini_country_list

    def test_forecast_shape(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """forecast_bhvar must return a DataFrame with correct structure.

        Checks:
        - 'iso3' and 'year' columns present
        - exactly horizon=5 unique future years
        - _mean, _lo80, _hi80 columns exist for each modeled indicator
        """
        result = fit_bhvar(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            n_samples=50,
            n_tune=50,
        )
        horizon = 5
        fc = forecast_bhvar(result, horizon=horizon, n_draws=20)

        # Required structural columns
        assert "iso3" in fc.columns, "Missing 'iso3' column in forecast"
        assert "year" in fc.columns, "Missing 'year' column in forecast"

        # Exactly horizon unique years
        n_years = fc["year"].nunique()
        assert n_years == horizon, (
            f"Expected {horizon} unique forecast years, got {n_years}"
        )

        # Determine which indicators are actually modeled (have parents in DAG)
        modeled = [ind for ind in mini_indicators if ind in mini_dag]
        for ind in modeled:
            for suffix in ("_mean", "_lo80", "_hi80"):
                col = f"{ind}{suffix}"
                assert col in fc.columns, (
                    f"Expected column '{col}' not found in forecast DataFrame"
                )

    def test_forecast_uncertainty_ordered(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """For every modeled indicator, lo80 <= mean <= hi80 must hold
        (with a tolerance of 1e-6 to accommodate floating-point rounding)."""
        result = fit_bhvar(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            n_samples=50,
            n_tune=50,
        )
        fc = forecast_bhvar(result, horizon=5, n_draws=20)

        modeled = [ind for ind in mini_indicators if ind in mini_dag]
        tol = 1e-6
        for ind in modeled:
            lo = fc[f"{ind}_lo80"].values
            mean = fc[f"{ind}_mean"].values
            hi = fc[f"{ind}_hi80"].values
            assert np.all(lo <= mean + tol), (
                f"{ind}: lo80 > mean (max violation: "
                f"{(lo - mean).max():.4e})"
            )
            assert np.all(mean <= hi + tol), (
                f"{ind}: mean > hi80 (max violation: "
                f"{(mean - hi).max():.4e})"
            )


class TestPosteriorExtraction:
    """Tests for extracting posterior summaries from a fitted BHVARResult."""

    def test_extract_posteriors_returns_dict(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """extract_posteriors must return a dict where each value has
        'mean' and 'sd' keys."""
        result = fit_bhvar(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            n_samples=50,
            n_tune=50,
        )
        posteriors = extract_posteriors(result)

        assert isinstance(posteriors, dict), "extract_posteriors must return a dict"
        assert len(posteriors) > 0, "Posteriors dict must not be empty"

        for param_name, summary in posteriors.items():
            assert "mean" in summary, (
                f"Parameter '{param_name}' missing 'mean' key"
            )
            assert "sd" in summary, (
                f"Parameter '{param_name}' missing 'sd' key"
            )
