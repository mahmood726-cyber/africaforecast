"""Tests for data ingestion: API fetching, panel assembly, checksumming."""

import hashlib
import json
import os
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest

from engine.config import COUNTRIES, INDICATOR_IDS
from engine.ingest import (
    fetch_world_bank,
    fetch_who_gho,
    build_panel,
    save_with_checksum,
    load_panel,
    compute_checksum,
    AFRICA_COUNTRY_CODES,
)


class TestWorldBankFetch:
    def test_returns_dataframe_with_required_columns(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 2},
            [
                {"countryiso3code": "NGA", "date": "2020",
                 "value": 52.1, "indicator": {"id": "SP.DYN.LE00.IN"}},
                {"countryiso3code": "KEN", "date": "2020",
                 "value": 66.3, "indicator": {"id": "SP.DYN.LE00.IN"}},
            ],
        ]
        with patch("engine.ingest.requests.get", return_value=mock_response):
            df = fetch_world_bank("SP.DYN.LE00.IN", "life_exp")
        assert set(df.columns) >= {"iso3", "year", "life_exp"}
        assert len(df) == 2
        assert df["life_exp"].dtype == np.float64

    def test_handles_null_values(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 1},
            [{"countryiso3code": "NGA", "date": "2020",
              "value": None, "indicator": {"id": "X"}}],
        ]
        with patch("engine.ingest.requests.get", return_value=mock_response):
            df = fetch_world_bank("X", "test_ind")
        assert len(df) == 1
        assert pd.isna(df["test_ind"].iloc[0])


class TestWhoGhoFetch:
    def test_returns_dataframe_with_required_columns(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {"SpatialDim": "NGA", "TimeDim": 2020,
                 "NumericValue": 4.5, "IndicatorCode": "HWF_0001"},
                {"SpatialDim": "KEN", "TimeDim": 2020,
                 "NumericValue": 2.3, "IndicatorCode": "HWF_0001"},
            ]
        }
        with patch("engine.ingest.requests.get", return_value=mock_response):
            df = fetch_who_gho("HWF_0001", "physicians")
        assert set(df.columns) >= {"iso3", "year", "physicians"}
        assert len(df) == 2


class TestPanelBuilding:
    def test_build_panel_merges_correctly(self):
        df1 = pd.DataFrame({
            "iso3": ["NGA", "NGA", "KEN", "KEN"],
            "year": [2019, 2020, 2019, 2020],
            "life_exp": [54.0, 54.5, 66.0, 66.3],
        })
        df2 = pd.DataFrame({
            "iso3": ["NGA", "NGA", "KEN", "KEN"],
            "year": [2019, 2020, 2019, 2020],
            "gdp_pc": [5000, 5100, 4000, 4100],
        })
        panel = build_panel([df1, df2])
        assert panel.shape == (4, 4)
        assert not panel.isnull().any().any()

    def test_build_panel_preserves_nans_on_partial_overlap(self):
        df1 = pd.DataFrame({
            "iso3": ["NGA", "NGA"], "year": [2019, 2020], "life_exp": [54.0, 54.5],
        })
        df2 = pd.DataFrame({
            "iso3": ["NGA", "KEN"], "year": [2020, 2020], "gdp_pc": [5100, 4100],
        })
        panel = build_panel([df1, df2])
        assert pd.isna(panel.loc[
            (panel["iso3"] == "NGA") & (panel["year"] == 2019), "gdp_pc"
        ].iloc[0])


class TestChecksum:
    def test_compute_checksum_deterministic(self, tmp_path):
        fpath = tmp_path / "test.csv"
        fpath.write_text("a,b\n1,2\n3,4")
        c1 = compute_checksum(str(fpath))
        c2 = compute_checksum(str(fpath))
        assert c1 == c2
        assert len(c1) == 64

    def test_save_with_checksum_creates_manifest(self, tmp_path):
        df = pd.DataFrame({"iso3": ["NGA"], "year": [2020], "x": [1.0]})
        save_with_checksum(df, str(tmp_path / "test.csv"), source="WB",
                           query="SP.DYN.LE00.IN")
        assert (tmp_path / "test.csv").exists()
        manifest = json.loads((tmp_path / "test.csv.manifest.json").read_text())
        assert "checksum" in manifest
        assert manifest["source"] == "WB"
