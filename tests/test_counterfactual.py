"""
Tests for engine/counterfactual.py — do-operator counterfactual simulation.

TDD: written before implementation.
"""

import pytest
import pandas as pd
import numpy as np

from engine.counterfactual import (
    simulate_counterfactual,
    precompute_intervention_grid,
    interpolate_intervention,
    CounterfactualResult,
)


# ---------------------------------------------------------------------------
# Class 1: Core simulation tests
# ---------------------------------------------------------------------------

class TestCounterfactual:
    """Tests for simulate_counterfactual."""

    def test_clamped_variable_stays_at_intervention(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        Intervene on gdp_pc with multiply=2.0 for NGA, horizon=5.
        Counterfactual gdp_pc_mean should be higher than baseline.
        """
        result = simulate_counterfactual(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=["NGA"],
            intervention={"gdp_pc": 2.0},
            intervention_type="multiply",
            horizon=5,
        )

        assert isinstance(result, CounterfactualResult)

        cf = result.counterfactual
        bl = result.baseline

        nga_cf = cf[cf["iso3"] == "NGA"]
        nga_bl = bl[bl["iso3"] == "NGA"]

        assert len(nga_cf) > 0, "Counterfactual must have NGA rows"
        assert len(nga_bl) > 0, "Baseline must have NGA rows"

        cf_gdp_mean = nga_cf["gdp_pc_mean"].mean()
        bl_gdp_mean = nga_bl["gdp_pc_mean"].mean()

        assert cf_gdp_mean > bl_gdp_mean, (
            f"Counterfactual gdp_pc_mean ({cf_gdp_mean:.2f}) should exceed "
            f"baseline ({bl_gdp_mean:.2f}) after 2x intervention"
        )

    def test_causal_children_affected(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        Intervene on physicians x3.0 for KEN.
        u5_mort (child with sign=-1) should decrease (cf <= baseline + tolerance).
        """
        result = simulate_counterfactual(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=["KEN"],
            intervention={"physicians": 3.0},
            intervention_type="multiply",
            horizon=10,
        )

        cf = result.counterfactual
        bl = result.baseline

        ken_cf = cf[cf["iso3"] == "KEN"]
        ken_bl = bl[bl["iso3"] == "KEN"]

        # u5_mort should be lower (or at most marginally higher due to noise)
        # with triple physicians (sign = -1 in mini_dag)
        cf_u5 = ken_cf["u5_mort_mean"].mean()
        bl_u5 = ken_bl["u5_mort_mean"].mean()

        tolerance = 5.0  # allow small noise
        assert cf_u5 <= bl_u5 + tolerance, (
            f"u5_mort counterfactual ({cf_u5:.2f}) should be <= baseline ({bl_u5:.2f}) "
            f"+ tolerance ({tolerance}) after tripling physicians"
        )

    def test_returns_baseline_and_counterfactual(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        Both DataFrames exist and have same length.
        """
        result = simulate_counterfactual(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            intervention={"gdp_pc": 1.5},
            intervention_type="multiply",
            horizon=5,
        )

        assert isinstance(result.baseline, pd.DataFrame), "baseline must be a DataFrame"
        assert isinstance(result.counterfactual, pd.DataFrame), "counterfactual must be a DataFrame"
        assert len(result.baseline) > 0, "baseline must not be empty"
        assert len(result.counterfactual) == len(result.baseline), (
            "baseline and counterfactual must have the same number of rows"
        )

    def test_result_has_ci_columns(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        For each {ind}_mean column, {ind}_lo80 and {ind}_hi80 must also exist.
        """
        result = simulate_counterfactual(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=["NGA"],
            intervention={"gdp_pc": 1.5},
            intervention_type="multiply",
            horizon=5,
        )

        cf = result.counterfactual
        mean_cols = [c for c in cf.columns if c.endswith("_mean")]
        assert len(mean_cols) > 0, "Must have at least one _mean column"

        for col in mean_cols:
            ind = col[: -len("_mean")]
            lo_col = f"{ind}_lo80"
            hi_col = f"{ind}_hi80"
            assert lo_col in cf.columns, f"Missing {lo_col}"
            assert hi_col in cf.columns, f"Missing {hi_col}"


# ---------------------------------------------------------------------------
# Class 2: Intervention grid tests
# ---------------------------------------------------------------------------

class TestInterventionGrid:
    """Tests for precompute_intervention_grid and interpolate_intervention."""

    def test_grid_produces_results_for_each_combo(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        grid_spec={"gdp_pc": [1.5, 2.0]} → 2 results returned.
        """
        grid_spec = {"gdp_pc": [1.5, 2.0]}

        grid = precompute_intervention_grid(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=["NGA"],
            grid_spec=grid_spec,
            horizon=5,
        )

        assert isinstance(grid, dict), "precompute_intervention_grid must return a dict"
        assert len(grid) == 2, f"Expected 2 grid results, got {len(grid)}"

        expected_keys = {"gdp_pc_1.5", "gdp_pc_2.0"}
        assert set(grid.keys()) == expected_keys, (
            f"Expected keys {expected_keys}, got {set(grid.keys())}"
        )

        for key, res in grid.items():
            assert isinstance(res, CounterfactualResult), (
                f"Grid entry {key} must be a CounterfactualResult"
            )
