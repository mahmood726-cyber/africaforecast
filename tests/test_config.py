"""Tests for config module: country coverage, indicator counts, region consistency."""

from engine.config import (
    COUNTRIES, REGIONS, COUNTRY_REGION, ALL_INDICATORS, INDICATOR_IDS,
    COMPREHENSIVE_INDICATORS, DISEASE_INDICATORS, SYSTEMS_INDICATORS,
    COVARIATES, PILOT_DOMAINS, SDG_TARGETS_2030, INTERVENTION_GRID,
)


def test_54_countries():
    assert len(COUNTRIES) == 54


def test_all_countries_in_exactly_one_region():
    region_countries = set()
    for codes in REGIONS.values():
        for code in codes:
            assert code not in region_countries, f"{code} in multiple regions"
            region_countries.add(code)
    assert region_countries == set(COUNTRIES.keys())


def test_country_region_mapping_complete():
    for iso3 in COUNTRIES:
        assert iso3 in COUNTRY_REGION, f"{iso3} missing from COUNTRY_REGION"


def test_five_regions():
    assert set(REGIONS.keys()) == {"North", "West", "Central", "East", "Southern"}


def test_comprehensive_indicator_count():
    assert len(COMPREHENSIVE_INDICATORS) == 10


def test_disease_indicator_count():
    assert len(DISEASE_INDICATORS) == 15


def test_systems_indicator_count():
    assert len(SYSTEMS_INDICATORS) == 12


def test_covariate_count():
    assert len(COVARIATES) == 15


def test_total_indicator_count():
    assert len(ALL_INDICATORS) == 52


def test_no_duplicate_indicator_ids():
    assert len(INDICATOR_IDS) == len(set(INDICATOR_IDS))


def test_pilot_domains_cover_non_covariates():
    domain_ids = set()
    for ids in PILOT_DOMAINS.values():
        domain_ids.update(ids)
    non_cov = set(INDICATOR_IDS) - {c[0] for c in COVARIATES}
    assert domain_ids == non_cov


def test_sdg_targets_reference_valid_indicators():
    for ind_id in SDG_TARGETS_2030:
        assert ind_id in INDICATOR_IDS, f"SDG target {ind_id} not in indicators"


def test_intervention_grid_references_valid_indicators():
    for ind_id in INTERVENTION_GRID:
        assert ind_id in INDICATOR_IDS, f"Intervention {ind_id} not in indicators"


def test_indicator_tuples_have_five_fields():
    for ind in ALL_INDICATORS:
        assert len(ind) == 5, f"Indicator {ind[0]} has {len(ind)} fields, expected 5"
