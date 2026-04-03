"""
AfricaForecast data ingestion layer.

Fetches from:
- World Bank WDI API (REST JSON)
- WHO Global Health Observatory API (OData)
- IHME GBD CSV files (pre-downloaded)

All outputs include SHA-256 checksums and JSON manifests for TruthCert compliance.
"""

import datetime
import hashlib
import json
import logging
import os
from typing import List, Optional

import pandas as pd
import requests

from engine.config import COUNTRIES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Country code list (sorted) — all 54 AU member states
# ---------------------------------------------------------------------------
AFRICA_COUNTRY_CODES: List[str] = sorted(COUNTRIES.keys())

# ---------------------------------------------------------------------------
# Indicator maps: our internal ID → source-specific code
# ---------------------------------------------------------------------------

WB_INDICATOR_MAP = {
    "life_exp":     "SP.DYN.LE00.IN",
    "u5_mort":      "SH.DYN.MORT",
    "neo_mort":     "SH.DYN.NMRT",
    "mat_mort":     "SH.STA.MMRT",
    "infant_mort":  "SP.DYN.IMRT.IN",
    "crude_death":  "SP.DYN.CDRT.IN",
    "adult_mort":   "SP.DYN.AMRT.P3",
    "hiv_prev":     "SH.DYN.AIDS.ZS",
    "beds":         "SH.MED.BEDS.ZS",
    "che_gdp":      "SH.XPD.CHEX.GD.ZS",
    "che_pc":       "SH.XPD.CHEX.PP.CD",
    "sba":          "SH.STA.BRTC.ZS",
    "oop_share":    "SH.XPD.OOPC.CH.ZS",
    "gdp_pc":       "NY.GDP.PCAP.PP.CD",
    "schooling":    "SE.SCH.LIFE",
    "urban":        "SP.URB.TOTL.IN.ZS",
    "pop_growth":   "SP.POP.GROW",
    "fertility":    "SP.DYN.TFRT.IN",
    "governance":   "GE.EST",
    "water":        "SH.H2O.SMDW.ZS",
    "sanitation":   "SH.STA.SMSS.ZS",
    "fem_edu":      "SE.SEC.ENRR.FE",
    "internet":     "IT.NET.USER.ZS",
    "agri_emp":     "SL.AGR.EMPL.ZS",
    "fdi":          "BX.KLT.DINV.WD.GD.ZS",
}

WHO_INDICATOR_MAP = {
    "ncd_mort":     "NCDMORT3070",
    "hale":         "WHOSIS_000002",
    "physicians":   "HWF_0001",
    "nurses":       "HWF_0002",
    "uhc_index":    "UHC_INDEX_REPORTED",
    "dtp3":         "WHS4_100",
    "diabetes":     "NCD_GLUC_04",
    "hypertension": "NCD_HYP_PREVALENCE_A",
    "tobacco":      "M_Est_smk_curr_std",
    "obesity":      "NCD_BMI_30A",
    "gghe":         "GHED_GGHE-DGDP_SHA2011",
    "ext_he":       "GHED_EXT_SHA2011PCT",
    "medicines":    "EmergPrepScore_IHR13",
    "mal_inc":      "MALARIA_EST_INCIDENCE",
    "tb_inc":       "MDG_0000000020",
}

IHME_INDICATORS = [
    "dalys_all", "hiv_inc", "mal_mort", "tb_mort",
    "lri_mort", "diarrhea_mort", "cvd_dalys", "cancer_dalys",
    "mental_dalys", "dah",
]

# Base URLs
_WB_BASE = "https://api.worldbank.org/v2/country/{codes}/indicator/{indicator}"
_WHO_BASE = "https://ghoapi.azureedge.net/api/{indicator_code}"


# ---------------------------------------------------------------------------
# World Bank fetch
# ---------------------------------------------------------------------------

def fetch_world_bank(
    wb_code: str,
    our_id: str,
    start_year: int = 1990,
    end_year: int = 2023,
) -> pd.DataFrame:
    """
    Fetch one WB WDI indicator for all African countries.

    Parameters
    ----------
    wb_code : str
        World Bank indicator code, e.g. "SP.DYN.LE00.IN".
    our_id : str
        Internal column name for the indicator value.
    start_year, end_year : int
        Date range for the query.

    Returns
    -------
    pd.DataFrame with columns ["iso3", "year", our_id].
    Values that are None in the API become NaN (float).
    Only rows whose iso3 is in COUNTRIES are returned.
    """
    codes_str = ";".join(AFRICA_COUNTRY_CODES)
    url = _WB_BASE.format(codes=codes_str, indicator=wb_code)
    params = {
        "format": "json",
        "per_page": 10000,
        "date": f"{start_year}:{end_year}",
    }
    logger.debug("WB fetch: %s %s", url, params)
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    payload = response.json()
    # WB returns list: [metadata_dict, records_list]
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Unexpected WB API response structure for {wb_code}")

    records = payload[1]
    if not records:
        logger.warning("WB returned 0 records for %s", wb_code)
        return pd.DataFrame(columns=["iso3", "year", our_id])

    rows = []
    for rec in records:
        iso3 = rec.get("countryiso3code", "")
        if iso3 not in COUNTRIES:
            continue
        year_str = rec.get("date", "")
        try:
            year = int(year_str)
        except (ValueError, TypeError):
            continue
        value = rec.get("value")
        rows.append({"iso3": iso3, "year": year, our_id: value})

    df = pd.DataFrame(rows, columns=["iso3", "year", our_id])
    df["year"] = df["year"].astype(int)
    df[our_id] = df[our_id].astype(float)
    return df


# ---------------------------------------------------------------------------
# WHO GHO fetch
# ---------------------------------------------------------------------------

def fetch_who_gho(who_code: str, our_id: str) -> pd.DataFrame:
    """
    Fetch one WHO GHO indicator for all African countries.

    Parameters
    ----------
    who_code : str
        WHO GHO indicator code, e.g. "HWF_0001".
    our_id : str
        Internal column name for the indicator value.

    Returns
    -------
    pd.DataFrame with columns ["iso3", "year", our_id].
    Only rows whose iso3 is in COUNTRIES are returned.
    """
    url = _WHO_BASE.format(indicator_code=who_code)
    logger.debug("WHO GHO fetch: %s", url)
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    payload = response.json()
    records = payload.get("value", [])
    if not records:
        logger.warning("WHO GHO returned 0 records for %s", who_code)
        return pd.DataFrame(columns=["iso3", "year", our_id])

    rows = []
    for rec in records:
        iso3 = rec.get("SpatialDim", "")
        if iso3 not in COUNTRIES:
            continue
        time_dim = rec.get("TimeDim")
        try:
            year = int(time_dim)
        except (ValueError, TypeError):
            continue
        value = rec.get("NumericValue")
        rows.append({"iso3": iso3, "year": year, our_id: value})

    df = pd.DataFrame(rows, columns=["iso3", "year", our_id])
    df["year"] = df["year"].astype(int)
    df[our_id] = pd.to_numeric(df[our_id], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# IHME CSV loader
# ---------------------------------------------------------------------------

def load_ihme_csv(
    filepath: str,
    our_id: str,
    value_col: str = "val",
) -> pd.DataFrame:
    """
    Load a pre-downloaded IHME GBD CSV file.

    Expected columns (at minimum): location_id or iso3, year, val.
    If an 'iso3' column is absent but 'ihme_loc_id' is present, uses the first
    3 characters as ISO3 (IHME uses e.g. "NGA" directly for most African countries).

    Parameters
    ----------
    filepath : str
        Path to the IHME CSV file.
    our_id : str
        Internal column name for the value.
    value_col : str
        Column name in the CSV that holds the numeric value.

    Returns
    -------
    pd.DataFrame with columns ["iso3", "year", our_id].
    """
    df_raw = pd.read_csv(filepath)

    # Resolve iso3 column
    if "iso3" in df_raw.columns:
        iso3_col = "iso3"
    elif "ihme_loc_id" in df_raw.columns:
        df_raw["iso3"] = df_raw["ihme_loc_id"].str[:3]
        iso3_col = "iso3"
    elif "location_name" in df_raw.columns:
        raise ValueError(
            "IHME CSV has location_name but no iso3/ihme_loc_id column. "
            "Provide a mapping or pre-process the file."
        )
    else:
        raise ValueError(f"Cannot determine iso3 column in {filepath}")

    # Resolve year column
    year_col = "year" if "year" in df_raw.columns else "year_id"
    if year_col not in df_raw.columns:
        raise ValueError(f"Cannot find year column in {filepath}")

    if value_col not in df_raw.columns:
        raise ValueError(f"Value column '{value_col}' not found in {filepath}")

    df = df_raw[[iso3_col, year_col, value_col]].copy()
    df = df.rename(columns={iso3_col: "iso3", year_col: "year", value_col: our_id})
    df = df[df["iso3"].isin(COUNTRIES)]
    df["year"] = df["year"].astype(int)
    df[our_id] = pd.to_numeric(df[our_id], errors="coerce")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Panel builder
# ---------------------------------------------------------------------------

def build_panel(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge a list of indicator DataFrames on (iso3, year) via full outer join.

    Each DataFrame must have at least columns ["iso3", "year"] plus one or more
    indicator columns. Partial overlaps result in NaN for missing combinations.

    Parameters
    ----------
    dataframes : list of pd.DataFrame

    Returns
    -------
    pd.DataFrame with columns ["iso3", "year", ...all indicators...]
    Sorted by (iso3, year).
    """
    if not dataframes:
        return pd.DataFrame(columns=["iso3", "year"])

    panel = dataframes[0].copy()
    for df in dataframes[1:]:
        # Identify new indicator columns (not iso3/year)
        new_cols = [c for c in df.columns if c not in ("iso3", "year")]
        merge_cols = ["iso3", "year"] + new_cols
        panel = panel.merge(df[merge_cols], on=["iso3", "year"], how="outer")

    panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
    return panel


# ---------------------------------------------------------------------------
# Checksum + manifest
# ---------------------------------------------------------------------------

def compute_checksum(filepath: str) -> str:
    """
    Compute SHA-256 hex digest of a file.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    str : 64-character hex string.
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def save_with_checksum(
    df: pd.DataFrame,
    filepath: str,
    source: str,
    query: str,
) -> str:
    """
    Save a DataFrame as CSV and write a companion JSON manifest.

    The manifest is written to ``filepath + '.manifest.json'`` and contains:
    - checksum (SHA-256 of the CSV)
    - source (e.g. "WB", "WHO", "IHME")
    - query (indicator code or filepath used to produce the data)
    - rows, columns counts
    - saved_at (ISO-8601 UTC timestamp)

    Parameters
    ----------
    df : pd.DataFrame
    filepath : str
    source : str
    query : str

    Returns
    -------
    str : SHA-256 checksum of the saved CSV.
    """
    df.to_csv(filepath, index=False)
    checksum = compute_checksum(filepath)

    manifest = {
        "checksum": checksum,
        "source": source,
        "query": query,
        "rows": len(df),
        "columns": list(df.columns),
        "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    manifest_path = filepath + ".manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    logger.info("Saved %s (%d rows) checksum=%s", filepath, len(df), checksum[:12])
    return checksum


def load_panel(filepath: str) -> pd.DataFrame:
    """
    Load a panel CSV previously saved with save_with_checksum.

    Verifies the SHA-256 checksum against the companion manifest if present.
    Raises ValueError if the checksum does not match.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(filepath)
    manifest_path = filepath + ".manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        expected = manifest.get("checksum", "")
        actual = compute_checksum(filepath)
        if expected and actual != expected:
            raise ValueError(
                f"Checksum mismatch for {filepath}: "
                f"expected {expected[:12]}... got {actual[:12]}..."
            )
    return df


# ---------------------------------------------------------------------------
# Full pipeline orchestrator
# ---------------------------------------------------------------------------

def ingest_all(
    data_dir: str,
    ihme_dir: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch all World Bank and WHO GHO indicators, optionally load IHME CSVs,
    then merge into a single country-year panel and save to disk.

    Parameters
    ----------
    data_dir : str
        Directory where raw CSV files and manifests will be written.
    ihme_dir : str, optional
        Directory containing pre-downloaded IHME GBD CSV files named
        ``{our_id}.csv``. If None, IHME indicators are skipped.

    Returns
    -------
    pd.DataFrame : merged panel with all available indicators.
    """
    os.makedirs(data_dir, exist_ok=True)
    dfs = []

    # --- World Bank ---
    for our_id, wb_code in WB_INDICATOR_MAP.items():
        logger.info("Fetching WB %s (%s) …", our_id, wb_code)
        try:
            df = fetch_world_bank(wb_code, our_id)
            if not df.empty:
                out_path = os.path.join(data_dir, f"wb_{our_id}.csv")
                save_with_checksum(df, out_path, source="WB", query=wb_code)
                dfs.append(df)
        except Exception as exc:
            logger.warning("WB fetch failed for %s: %s", our_id, exc)

    # --- WHO GHO ---
    for our_id, who_code in WHO_INDICATOR_MAP.items():
        logger.info("Fetching WHO GHO %s (%s) …", our_id, who_code)
        try:
            df = fetch_who_gho(who_code, our_id)
            if not df.empty:
                out_path = os.path.join(data_dir, f"who_{our_id}.csv")
                save_with_checksum(df, out_path, source="WHO", query=who_code)
                dfs.append(df)
        except Exception as exc:
            logger.warning("WHO fetch failed for %s: %s", our_id, exc)

    # --- IHME CSV ---
    if ihme_dir is not None:
        for our_id in IHME_INDICATORS:
            csv_path = os.path.join(ihme_dir, f"{our_id}.csv")
            if not os.path.exists(csv_path):
                logger.warning("IHME CSV not found: %s", csv_path)
                continue
            logger.info("Loading IHME %s …", our_id)
            try:
                df = load_ihme_csv(csv_path, our_id)
                if not df.empty:
                    out_path = os.path.join(data_dir, f"ihme_{our_id}.csv")
                    save_with_checksum(df, out_path, source="IHME", query=csv_path)
                    dfs.append(df)
            except Exception as exc:
                logger.warning("IHME load failed for %s: %s", our_id, exc)

    if not dfs:
        logger.warning("No data fetched — returning empty panel.")
        return pd.DataFrame(columns=["iso3", "year"])

    panel = build_panel(dfs)
    panel_path = os.path.join(data_dir, "panel.csv")
    save_with_checksum(panel, panel_path, source="merged", query="ingest_all")
    logger.info("Panel saved: %d rows × %d cols", *panel.shape)
    return panel
