"""
AfricaForecast — End-to-End Pipeline Orchestrator.

Runs the full pipeline:
    ingest → causal DAG → ensemble forecast → counterfactual grid →
    holdout validation → JSON bundle export

Usage
-----
    python -m engine.run_pipeline [options]
    python engine/run_pipeline.py [options]

Options
-------
    --skip-ingest       Skip data download; load existing data/panel.csv
    --mini              Use a 10-country subset (faster development runs)
    --skip-bhvar        Placeholder flag (BHVAR is not used in ensemble path)
    --data-dir DIR      Directory for raw data files  [default: data]
    --results-dir DIR   Directory for output artefacts [default: results]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conditional import: validate module may not exist yet (Task 7)
# ---------------------------------------------------------------------------
try:
    from engine.validate import run_holdout_validation  # type: ignore
    _VALIDATE_AVAILABLE = True
except ImportError:
    _VALIDATE_AVAILABLE = False
    logger.warning(
        "engine.validate not found — validation step will be skipped. "
        "Implement Task 7 to enable holdout validation."
    )

# ---------------------------------------------------------------------------
# Core imports (always required)
# ---------------------------------------------------------------------------
from engine.config import (
    COUNTRIES,
    FORECAST_HORIZON,
    INDICATOR_IDS,
    INDICATOR_NAMES,
    INTERVENTION_GRID,
    PILOT_DOMAINS,
    REGIONS,
    COUNTRY_REGION,
    SDG_TARGETS_2030,
    SEED,
    TRAIN_END,
    VALIDATE_END,
    COMPREHENSIVE_INDICATORS,
    DISEASE_INDICATORS,
    SYSTEMS_INDICATORS,
    COVARIATES,
)
from engine.ingest import ingest_all, load_panel
from engine.causal_graph import (
    build_domain_dag,
    refine_with_discovery,
    save_dag,
    topological_sort,
)
from engine.ensemble import ensemble_forecast
from engine.counterfactual import precompute_intervention_grid


# ---------------------------------------------------------------------------
# Mini-country subset (10 countries, one per sub-region)
# ---------------------------------------------------------------------------
_MINI_COUNTRIES: List[str] = [
    "NGA",  # West   — Nigeria
    "GHA",  # West   — Ghana
    "ETH",  # East   — Ethiopia
    "KEN",  # East   — Kenya
    "ZAF",  # South  — South Africa
    "EGY",  # North  — Egypt
    "CMR",  # Central — Cameroon
    "COD",  # Central — DR Congo
    "TZA",  # East   — Tanzania
    "SEN",  # West   — Senegal
]


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _df_to_records(df) -> List[Dict[str, Any]]:
    """Convert a DataFrame to a list of dicts, coercing NaN to None."""
    import math
    records = df.to_dict(orient="records")
    cleaned = []
    for row in records:
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                clean_row[k] = None
            else:
                clean_row[k] = v
        cleaned.append(clean_row)
    return cleaned


def _serialise_dag(dag: dict) -> Dict[str, Any]:
    """Convert DAG (child → [(parent, source, sign)]) to JSON-safe structure."""
    return {
        child: [[p, s, int(sgn)] for p, s, sgn in parents]
        for child, parents in dag.items()
    }


def _serialise_counterfactuals(cf_grid: dict) -> Dict[str, Any]:
    """Flatten CounterfactualResult objects into JSON-safe dicts."""
    export: Dict[str, Any] = {}
    for key, result in cf_grid.items():
        export[key] = {
            "intervention": result.intervention,
            "intervention_type": result.intervention_type,
            "affected_indicators": result.affected_indicators,
            "baseline": _df_to_records(result.baseline),
            "counterfactual": _df_to_records(result.counterfactual),
        }
    return export


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_pipeline",
        description="AfricaForecast end-to-end pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        default=False,
        help="Skip data download; load existing panel.csv from --data-dir",
    )
    parser.add_argument(
        "--mini",
        action="store_true",
        default=False,
        help="Use a 10-country subset for fast development runs",
    )
    parser.add_argument(
        "--skip-bhvar",
        action="store_true",
        default=True,
        help="Skip BHVAR model (placeholder; BHVAR is not in the ensemble path)",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        metavar="DIR",
        help="Directory for raw / cached data files",
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        metavar="DIR",
        help="Directory for output artefacts (JSON bundle, DAG, etc.)",
    )
    return parser


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def step_ingest(data_dir: str, skip: bool) -> Any:
    """Step 1 — Ingest or load panel data."""
    panel_path = os.path.join(data_dir, "panel.csv")

    if skip:
        logger.info("[Step 1/6] Loading existing panel from %s …", panel_path)
        if not os.path.exists(panel_path):
            raise FileNotFoundError(
                f"--skip-ingest requested but panel not found at {panel_path}. "
                "Run without --skip-ingest first."
            )
        panel = load_panel(panel_path)
        logger.info("  Loaded panel: %d rows × %d cols", *panel.shape)
    else:
        logger.info("[Step 1/6] Downloading data from WB / WHO / IHME …")
        panel = ingest_all(data_dir=data_dir)
        logger.info("  Panel built: %d rows × %d cols", *panel.shape)

    return panel


def step_build_dag(panel: Any, indicators: List[str], results_dir: str) -> dict:
    """Step 2 — Build and optionally refine the causal DAG."""
    logger.info("[Step 2/6] Building domain DAG …")
    dag = build_domain_dag()
    n_edges_domain = sum(len(v) for v in dag.values())
    logger.info("  Domain DAG: %d nodes, %d edges", len(dag), n_edges_domain)

    logger.info("  Refining DAG with causal discovery (PC algorithm) …")
    dag = refine_with_discovery(dag, panel, indicators)
    n_edges_final = sum(len(v) for v in dag.values())
    n_data_edges = n_edges_final - n_edges_domain
    logger.info(
        "  Refined DAG: %d edges total (%d domain + %d data-driven)",
        n_edges_final,
        n_edges_domain,
        n_data_edges,
    )

    dag_path = os.path.join(results_dir, "dag_edges.json")
    save_dag(dag, dag_path)
    logger.info("  DAG saved to %s", dag_path)

    # Run topological sort to validate acyclicity
    topo = topological_sort(dag)
    logger.info("  Topological order verified (%d nodes)", len(topo))

    return dag


def step_ensemble(
    panel: Any,
    indicators: List[str],
    countries: List[str],
) -> Any:
    """Step 3 — Run ensemble forecast (Ridge + GP + ETS)."""
    logger.info(
        "[Step 3/6] Running ensemble forecast (%d indicators, %d countries) …",
        len(indicators),
        len(countries),
    )
    result = ensemble_forecast(
        panel=panel,
        indicators=indicators,
        countries=countries,
        train_end=TRAIN_END,
        val_end=VALIDATE_END,
        horizon=FORECAST_HORIZON,
    )
    logger.info(
        "  Ensemble done. Forecast rows: %d. Ensemble RMSE: %.4f",
        len(result.forecasts),
        result.ensemble_rmse,
    )
    for model, rmse in result.component_rmses.items():
        logger.info("    %-12s RMSE: %.4f", model, rmse)
    return result


def step_counterfactual(
    panel: Any,
    dag: dict,
    indicators: List[str],
    countries: List[str],
) -> dict:
    """Step 4 — Pre-compute counterfactual intervention grid."""
    n_scenarios = sum(len(v) for v in INTERVENTION_GRID.values())
    logger.info(
        "[Step 4/6] Pre-computing counterfactual grid (%d scenarios) …",
        n_scenarios,
    )
    cf_grid = precompute_intervention_grid(
        panel=panel,
        dag=dag,
        indicators=indicators,
        countries=countries,
        grid_spec=INTERVENTION_GRID,
        horizon=FORECAST_HORIZON,
    )
    logger.info("  Counterfactual grid complete: %d entries", len(cf_grid))
    return cf_grid


def step_validate(
    panel: Any,
    indicators: List[str],
    countries: List[str],
) -> Dict[str, Any]:
    """Step 5 — Run holdout validation (skipped if module not available)."""
    if not _VALIDATE_AVAILABLE:
        logger.info(
            "[Step 5/6] Validation SKIPPED — engine.validate not yet implemented."
        )
        return {
            "status": "skipped",
            "reason": "engine.validate module not available (Task 7 pending)",
        }

    logger.info("[Step 5/6] Running holdout validation …")
    try:
        val_result = run_holdout_validation(
            panel=panel,
            indicators=indicators,
            countries=countries,
            train_end=TRAIN_END,
            val_end=VALIDATE_END,
        )
        logger.info("  Validation complete.")
        # Attempt to serialise; fall back to str representation
        if hasattr(val_result, "to_dict"):
            return val_result.to_dict()
        elif isinstance(val_result, dict):
            return val_result
        else:
            return {"result": str(val_result)}
    except Exception as exc:
        logger.warning("  Validation raised an exception: %s", exc)
        return {"status": "error", "reason": str(exc)}


def step_export(
    results_dir: str,
    countries: List[str],
    indicators: List[str],
    panel: Any,
    ensemble_result: Any,
    cf_grid: dict,
    val_export: Dict[str, Any],
    dag: dict,
) -> str:
    """Step 6 — Assemble and write the master JSON bundle."""
    logger.info("[Step 6/6] Exporting master JSON bundle …")

    # Serialise ensemble weights (keys may be indicator IDs → model → float)
    weights_export = ensemble_result.weights

    # Serialise forecasts DataFrame
    forecast_data = _df_to_records(ensemble_result.forecasts)

    # Serialise historical panel
    hist_data = _df_to_records(panel)

    bundle = {
        "meta": {
            "project": "AfricaForecast",
            "version": "1.0.0",
            "countries": countries,
            "indicators": indicators,
            "indicator_names": INDICATOR_NAMES,
            "regions": REGIONS,
            "country_region": COUNTRY_REGION,
            "pilot_domains": PILOT_DOMAINS,
            "sdg_targets": SDG_TARGETS_2030,
            "train_end": TRAIN_END,
            "validate_end": VALIDATE_END,
            "forecast_horizon": FORECAST_HORIZON,
            "seed": SEED,
        },
        "historical": hist_data,
        "forecasts": forecast_data,
        "counterfactuals": _serialise_counterfactuals(cf_grid),
        "validation": val_export,
        "dag": _serialise_dag(dag),
        "ensemble_weights": weights_export,
    }

    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "forecasts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=1, default=str)

    size_kb = os.path.getsize(out_path) / 1024
    logger.info("  Bundle saved: %s  (%.1f KB)", out_path, size_kb)
    return out_path


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    t0 = time.time()

    logger.info("=" * 60)
    logger.info("AfricaForecast Pipeline  |  seed=%d", SEED)
    logger.info(
        "Countries: %s  |  Indicators: %d",
        "10-country mini" if args.mini else f"all {len(COUNTRIES)}",
        len(INDICATOR_IDS),
    )
    logger.info("=" * 60)

    # Resolve country list
    countries: List[str] = (
        _MINI_COUNTRIES if args.mini else sorted(COUNTRIES.keys())
    )
    indicators: List[str] = INDICATOR_IDS

    # Resolve paths (make absolute if relative, relative to cwd)
    data_dir = os.path.abspath(args.data_dir)
    results_dir = os.path.abspath(args.results_dir)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # --- Step 1: Ingest ---
    panel = step_ingest(data_dir=data_dir, skip=args.skip_ingest)

    # --- Step 2: Causal DAG ---
    dag = step_build_dag(panel=panel, indicators=indicators, results_dir=results_dir)

    # --- Step 3: Ensemble forecast ---
    ensemble_result = step_ensemble(
        panel=panel,
        indicators=indicators,
        countries=countries,
    )

    # --- Step 4: Counterfactual grid ---
    cf_grid = step_counterfactual(
        panel=panel,
        dag=dag,
        indicators=indicators,
        countries=countries,
    )

    # --- Step 5: Holdout validation ---
    val_export = step_validate(
        panel=panel,
        indicators=indicators,
        countries=countries,
    )

    # --- Step 6: Export JSON bundle ---
    out_path = step_export(
        results_dir=results_dir,
        countries=countries,
        indicators=indicators,
        panel=panel,
        ensemble_result=ensemble_result,
        cf_grid=cf_grid,
        val_export=val_export,
        dag=dag,
    )

    elapsed = time.time() - t0
    logger.info("=" * 60)
    logger.info("Pipeline complete in %.1f s", elapsed)
    logger.info("Output: %s", out_path)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
