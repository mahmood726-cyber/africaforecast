"""Shared test fixtures for AfricaForecast test suite."""

import numpy as np
import pandas as pd
import pytest

from engine.config import (
    COUNTRIES, REGIONS, COUNTRY_REGION, INDICATOR_IDS,
    COMPREHENSIVE_INDICATORS, DISEASE_INDICATORS,
    SYSTEMS_INDICATORS, COVARIATES, SEED,
)


@pytest.fixture
def rng():
    """Seeded random generator for reproducible tests."""
    return np.random.default_rng(SEED)


@pytest.fixture
def mini_countries():
    """Small subset of countries for fast tests (2 per region)."""
    return {
        "North": ["EGY", "MAR"],
        "West": ["NGA", "GHA"],
        "Central": ["CMR", "COD"],
        "East": ["KEN", "ETH"],
        "Southern": ["ZAF", "BWA"],
    }


@pytest.fixture
def mini_country_list(mini_countries):
    """Flat list of 10 test countries."""
    return [c for codes in mini_countries.values() for c in codes]


@pytest.fixture
def mini_indicators():
    """Small indicator subset for fast tests (2 per domain + 2 covariates)."""
    return ["life_exp", "u5_mort", "hiv_inc", "mal_mort",
            "physicians", "uhc_index", "gdp_pc", "schooling"]


@pytest.fixture
def synthetic_panel(rng, mini_country_list, mini_indicators):
    """
    Synthetic country-year panel: 10 countries x 30 years x 8 indicators.
    Values are smooth trends + noise so models can fit.
    """
    years = list(range(1992, 2022))
    rows = []
    for iso3 in mini_country_list:
        base = rng.uniform(10, 100, size=len(mini_indicators))
        trend = rng.uniform(-0.5, 0.5, size=len(mini_indicators))
        for t_idx, year in enumerate(years):
            vals = base + trend * t_idx + rng.normal(0, 1, size=len(mini_indicators))
            row = {"iso3": iso3, "year": year}
            for i, ind_id in enumerate(mini_indicators):
                row[ind_id] = float(np.clip(vals[i], 0.1, 999))
            rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture
def mini_dag(mini_indicators):
    """
    Small causal DAG for testing. Edges represent plausible causal links.
    Returns dict: {child: [(parent, source, sign), ...]}
    """
    return {
        "u5_mort": [
            ("gdp_pc", "domain", -1),
            ("physicians", "domain", -1),
        ],
        "life_exp": [
            ("gdp_pc", "domain", 1),
            ("u5_mort", "domain", -1),
        ],
        "hiv_inc": [
            ("gdp_pc", "domain", -1),
            ("schooling", "domain", -1),
        ],
        "mal_mort": [
            ("gdp_pc", "domain", -1),
            ("uhc_index", "domain", -1),
        ],
        "physicians": [
            ("gdp_pc", "domain", 1),
            ("schooling", "domain", 1),
        ],
        "uhc_index": [
            ("physicians", "domain", 1),
            ("gdp_pc", "domain", 1),
        ],
    }


@pytest.fixture
def mock_posterior(rng, mini_country_list, mini_indicators, mini_dag):
    """
    Mock posterior samples for BHVAR coefficients.
    Shape: dict of parameter_name -> (n_samples, ...) arrays.
    """
    n_samples = 100
    posteriors = {}

    # Beta coefficients: one per (child, parent) edge
    for child, parents in mini_dag.items():
        for parent, source, sign in parents:
            key = f"beta_{child}_{parent}"
            mean = sign * rng.uniform(0.05, 0.3)
            posteriors[key] = rng.normal(mean, 0.05, size=n_samples)

    # Country intercepts
    for iso3 in mini_country_list:
        for ind in mini_indicators:
            key = f"alpha_{ind}_{iso3}"
            posteriors[key] = rng.normal(0, 1, size=n_samples)

    # Trend
    for ind in mini_indicators:
        key = f"delta_{ind}"
        posteriors[key] = rng.normal(0, 0.01, size=n_samples)

    return posteriors
