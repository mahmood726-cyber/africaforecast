"""
Tests for the Validation Module: metrics, calibration, naive benchmark, holdout pipeline.
"""

import numpy as np
import pytest

from engine.validate import (
    compute_rmse,
    compute_mae,
    compute_coverage,
    compute_calibration,
    benchmark_vs_naive,
    ValidationReport,
    run_holdout_validation,
)


class TestMetrics:
    """Unit tests for scalar metric functions."""

    def test_rmse_perfect(self):
        """RMSE of identical arrays is 0."""
        actual = [1.0, 2.0, 3.0]
        predicted = [1.0, 2.0, 3.0]
        assert compute_rmse(actual, predicted) == 0.0

    def test_rmse_known_value(self):
        """RMSE([1,2,3], [2,3,4]) == 1.0."""
        actual = [1.0, 2.0, 3.0]
        predicted = [2.0, 3.0, 4.0]
        result = compute_rmse(actual, predicted)
        assert abs(result - 1.0) < 1e-9, f"Expected 1.0, got {result}"

    def test_mae_known_value(self):
        """MAE([1,2,3], [2,3,4]) == 1.0."""
        actual = [1.0, 2.0, 3.0]
        predicted = [2.0, 3.0, 4.0]
        result = compute_mae(actual, predicted)
        assert abs(result - 1.0) < 1e-9, f"Expected 1.0, got {result}"

    def test_coverage_perfect(self):
        """Coverage is 1.0 when all actuals lie within [lo, hi]."""
        actual = [1.0, 2.0, 3.0]
        lo = [0.0, 1.0, 2.0]
        hi = [2.0, 3.0, 4.0]
        result = compute_coverage(actual, lo, hi)
        assert result == 1.0, f"Expected 1.0, got {result}"

    def test_coverage_none(self):
        """Coverage is 0.0 when no actuals lie within [lo, hi]."""
        actual = [10.0, 20.0, 30.0]
        lo = [0.0, 0.0, 0.0]
        hi = [5.0, 5.0, 5.0]
        result = compute_coverage(actual, lo, hi)
        assert result == 0.0, f"Expected 0.0, got {result}"

    def test_coverage_partial(self):
        """Coverage is 0.5 when exactly 1 of 2 actuals lies within [lo, hi]."""
        actual = [1.0, 10.0]
        lo = [0.0, 0.0]
        hi = [2.0, 5.0]
        result = compute_coverage(actual, lo, hi)
        assert abs(result - 0.5) < 1e-9, f"Expected 0.5, got {result}"


class TestCalibration:
    """Tests for calibration computation."""

    def test_calibration_returns_dict(self):
        """compute_calibration must return a dict with 'coverage_80' and 'coverage_95' keys."""
        actual = [1.0, 2.0, 3.0, 4.0, 5.0]
        lo80 = [0.5, 1.5, 2.5, 3.5, 4.5]
        hi80 = [1.5, 2.5, 3.5, 4.5, 5.5]
        lo95 = [0.0, 1.0, 2.0, 3.0, 4.0]
        hi95 = [2.0, 3.0, 4.0, 5.0, 6.0]
        result = compute_calibration(actual, lo80, hi80, lo95, hi95)
        assert isinstance(result, dict), "compute_calibration must return a dict"
        assert "coverage_80" in result, "Missing 'coverage_80' key"
        assert "coverage_95" in result, "Missing 'coverage_95' key"
        # Coverage values must be in [0, 1]
        assert 0.0 <= result["coverage_80"] <= 1.0
        assert 0.0 <= result["coverage_95"] <= 1.0


class TestHoldoutValidation:
    """Tests for the holdout validation pipeline."""

    def test_returns_validation_report(
        self, synthetic_panel, mini_dag, mini_indicators, mini_country_list
    ):
        """
        run_holdout_validation must return a ValidationReport with indicators_validated > 0.
        Uses a short train_end/val_end window to keep test runtime manageable.
        """
        report = run_holdout_validation(
            panel=synthetic_panel,
            dag=mini_dag,
            indicators=mini_indicators,
            countries=mini_country_list,
            train_end=2012,
            val_end=2015,
        )
        assert isinstance(report, ValidationReport), (
            f"Expected ValidationReport, got {type(report)}"
        )
        assert report.indicators_validated > 0, (
            "ValidationReport must have indicators_validated > 0"
        )
        assert report.overall_rmse >= 0.0, "overall_rmse must be non-negative"
        assert report.overall_mae >= 0.0, "overall_mae must be non-negative"
        assert 0.0 <= report.mean_coverage_80 <= 1.0, "mean_coverage_80 must be in [0,1]"
        assert 0.0 <= report.mean_coverage_95 <= 1.0, "mean_coverage_95 must be in [0,1]"
        assert report.countries_modeled > 0, "countries_modeled must be > 0"
