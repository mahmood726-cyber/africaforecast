"""
Integration tests for AfricaForecast — Task 10.

Verifies the full pipeline end-to-end:
  - DAG domain validity and acyclicity
  - Ensemble forecast on synthetic panel
  - Counterfactual simulation on synthetic panel
  - Holdout validation pipeline
  - JSON export structure
  - Config integrity (regions ↔ countries consistency)
"""

import json

import pytest

from engine.causal_graph import build_domain_dag, is_acyclic, dag_to_adjacency
from engine.config import COUNTRIES, REGIONS
from engine.counterfactual import simulate_counterfactual
from engine.ensemble import ensemble_forecast
from engine.validate import run_holdout_validation


# ---------------------------------------------------------------------------
# TestFullPipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_dag_domain_is_valid(self):
        dag = build_domain_dag()
        adj = dag_to_adjacency(dag)
        assert is_acyclic(adj)
        n_edges = sum(len(parents) for parents in dag.values())
        assert n_edges >= 30

    def test_ensemble_on_synthetic(self, synthetic_panel, mini_dag,
                                    mini_indicators, mini_country_list):
        result = ensemble_forecast(
            synthetic_panel, mini_indicators, mini_country_list,
            train_end=2015, val_end=2019, horizon=3,
        )
        assert len(result.forecasts) > 0
        assert result.ensemble_rmse < float("inf")

    def test_counterfactual_on_synthetic(self, synthetic_panel, mini_dag,
                                          mini_indicators, mini_country_list):
        result = simulate_counterfactual(
            synthetic_panel, mini_dag, mini_indicators, mini_country_list,
            intervention={"gdp_pc": 2.0},
            intervention_type="multiply",
            horizon=3,
        )
        assert len(result.baseline) > 0
        assert len(result.counterfactual) > 0
        assert len(result.affected_indicators) > 0

    def test_validation_on_synthetic(self, synthetic_panel, mini_dag,
                                      mini_indicators, mini_country_list):
        report = run_holdout_validation(
            synthetic_panel, mini_dag, mini_indicators, mini_country_list,
            train_end=2015, val_end=2019,
        )
        assert report.indicators_validated > 0
        assert report.overall_rmse < float("inf")

    def test_json_export_structure(self, synthetic_panel, mini_dag,
                                    mini_indicators, mini_country_list, tmp_path):
        from engine.ensemble import ensemble_forecast
        from engine.counterfactual import precompute_intervention_grid

        result = ensemble_forecast(
            synthetic_panel, mini_indicators, mini_country_list,
            train_end=2015, val_end=2019, horizon=3,
        )
        grid = precompute_intervention_grid(
            synthetic_panel, mini_dag, mini_indicators, ["NGA"],
            grid_spec={"gdp_pc": [1.5]}, horizon=3,
        )
        bundle = {
            "meta": {"project": "AfricaForecast", "countries": mini_country_list},
            "historical": synthetic_panel.to_dict(orient="records"),
            "forecasts": result.forecasts.to_dict(orient="records"),
            "counterfactuals": {
                k: {"baseline": v.baseline.to_dict(orient="records"),
                     "counterfactual": v.counterfactual.to_dict(orient="records")}
                for k, v in grid.items()
            },
        }
        out = tmp_path / "forecasts.json"
        with open(out, "w") as f:
            json.dump(bundle, f, default=str)
        loaded = json.loads(out.read_text())
        assert "meta" in loaded
        assert "historical" in loaded
        assert "forecasts" in loaded
        assert "counterfactuals" in loaded
        assert len(loaded["forecasts"]) > 0


# ---------------------------------------------------------------------------
# TestConfigIntegrity
# ---------------------------------------------------------------------------

class TestConfigIntegrity:

    def test_all_region_countries_are_valid(self):
        for region, codes in REGIONS.items():
            for code in codes:
                assert code in COUNTRIES

    def test_no_orphan_countries(self):
        assigned = set()
        for codes in REGIONS.values():
            assigned.update(codes)
        assert assigned == set(COUNTRIES.keys())
