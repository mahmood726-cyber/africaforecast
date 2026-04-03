"""
AfricaForecast configuration: countries, indicators, regions, targets.

All 54 African Union member states. Indicators grouped into three pilot
domains plus covariates. Regions follow AU geographic groupings.
"""

SEED = 42
TRAIN_END = 2015
VALIDATE_START = 2016
VALIDATE_END = 2021
FORECAST_START = 2022
FORECAST_END = 2036
FORECAST_HORIZON = FORECAST_END - VALIDATE_END  # 15 years from last data

# --- 54 AU member states (ISO3 codes) ---
COUNTRIES = {
    # North Africa
    "DZA": "Algeria", "EGY": "Egypt", "LBY": "Libya",
    "MRT": "Mauritania", "MAR": "Morocco", "TUN": "Tunisia",
    "SDN": "Sudan",
    # West Africa
    "BEN": "Benin", "BFA": "Burkina Faso", "CPV": "Cabo Verde",
    "CIV": "Cote d'Ivoire", "GMB": "Gambia", "GHA": "Ghana",
    "GIN": "Guinea", "GNB": "Guinea-Bissau", "LBR": "Liberia",
    "MLI": "Mali", "NER": "Niger", "NGA": "Nigeria",
    "SEN": "Senegal", "SLE": "Sierra Leone", "TGO": "Togo",
    # Central Africa
    "CMR": "Cameroon", "CAF": "Central African Republic",
    "TCD": "Chad", "COG": "Congo", "COD": "DR Congo",
    "GNQ": "Equatorial Guinea", "GAB": "Gabon",
    "STP": "Sao Tome and Principe",
    # East Africa
    "BDI": "Burundi", "COM": "Comoros", "DJI": "Djibouti",
    "ERI": "Eritrea", "ETH": "Ethiopia", "KEN": "Kenya",
    "MDG": "Madagascar", "MWI": "Malawi", "MUS": "Mauritius",
    "MOZ": "Mozambique", "RWA": "Rwanda", "SYC": "Seychelles",
    "SOM": "Somalia", "SSD": "South Sudan", "TZA": "Tanzania",
    "UGA": "Uganda",
    # Southern Africa
    "AGO": "Angola", "BWA": "Botswana", "SWZ": "Eswatini",
    "LSO": "Lesotho", "NAM": "Namibia", "ZAF": "South Africa",
    "ZMB": "Zambia", "ZWE": "Zimbabwe",
}

REGIONS = {
    "North": ["DZA", "EGY", "LBY", "MRT", "MAR", "TUN", "SDN"],
    "West": ["BEN", "BFA", "CPV", "CIV", "GMB", "GHA", "GIN", "GNB",
             "LBR", "MLI", "NER", "NGA", "SEN", "SLE", "TGO"],
    "Central": ["CMR", "CAF", "TCD", "COG", "COD", "GNQ", "GAB", "STP"],
    "East": ["BDI", "COM", "DJI", "ERI", "ETH", "KEN", "MDG", "MWI",
             "MUS", "MOZ", "RWA", "SYC", "SOM", "SSD", "TZA", "UGA"],
    "Southern": ["AGO", "BWA", "SWZ", "LSO", "NAM", "ZAF", "ZMB", "ZWE"],
}

# Map each country to its region
COUNTRY_REGION = {}
for region, codes in REGIONS.items():
    for code in codes:
        COUNTRY_REGION[code] = region


# --- Indicator definitions ---
# Each indicator: (id, name, source, unit, direction)
# direction: "lower_better" or "higher_better" (for SDG target evaluation)

COMPREHENSIVE_INDICATORS = [
    ("life_exp", "Life expectancy at birth", "WB", "years", "higher_better"),
    ("u5_mort", "Under-5 mortality rate", "WB", "per 1000 live births", "lower_better"),
    ("neo_mort", "Neonatal mortality rate", "WB", "per 1000 live births", "lower_better"),
    ("mat_mort", "Maternal mortality ratio", "WB", "per 100K live births", "lower_better"),
    ("ncd_mort", "NCD mortality 30-70 age-std", "WHO", "probability %", "lower_better"),
    ("dalys_all", "All-cause DALYs", "IHME", "per 100K", "lower_better"),
    ("hale", "Healthy life expectancy", "WHO", "years", "higher_better"),
    ("adult_mort", "Adult mortality 15-60", "WB", "per 1000", "lower_better"),
    ("infant_mort", "Infant mortality rate", "WB", "per 1000 live births", "lower_better"),
    ("crude_death", "Crude death rate", "WB", "per 1000", "lower_better"),
]

DISEASE_INDICATORS = [
    ("hiv_inc", "HIV incidence", "IHME", "per 1000", "lower_better"),
    ("hiv_prev", "HIV prevalence 15-49", "WB", "%", "lower_better"),
    ("mal_inc", "Malaria incidence", "WHO", "per 1000 at risk", "lower_better"),
    ("mal_mort", "Malaria mortality", "IHME", "per 100K", "lower_better"),
    ("tb_inc", "TB incidence", "WHO", "per 100K", "lower_better"),
    ("tb_mort", "TB mortality", "IHME", "per 100K", "lower_better"),
    ("diabetes", "Diabetes prevalence", "WHO", "%", "lower_better"),
    ("hypertension", "Hypertension prevalence", "WHO", "%", "lower_better"),
    ("tobacco", "Tobacco use prevalence", "WHO", "%", "lower_better"),
    ("obesity", "Obesity prevalence", "WHO", "%", "lower_better"),
    ("lri_mort", "Lower resp infection mortality", "IHME", "per 100K", "lower_better"),
    ("diarrhea_mort", "Diarrhoeal disease mortality", "IHME", "per 100K", "lower_better"),
    ("cvd_dalys", "Cardiovascular DALYs", "IHME", "per 100K", "lower_better"),
    ("cancer_dalys", "Cancer DALYs", "IHME", "per 100K", "lower_better"),
    ("mental_dalys", "Mental health DALYs", "IHME", "per 100K", "lower_better"),
]

SYSTEMS_INDICATORS = [
    ("physicians", "Physician density", "WHO", "per 10K", "higher_better"),
    ("nurses", "Nurse/midwife density", "WHO", "per 10K", "higher_better"),
    ("beds", "Hospital bed density", "WB", "per 1000", "higher_better"),
    ("che_gdp", "Health expenditure % GDP", "WB", "%", "higher_better"),
    ("che_pc", "Health expenditure per capita PPP", "WB", "USD", "higher_better"),
    ("uhc_index", "UHC service coverage index", "WHO", "0-100", "higher_better"),
    ("dtp3", "DTP3 immunization coverage", "WHO", "%", "higher_better"),
    ("sba", "Skilled birth attendance", "WB", "%", "higher_better"),
    ("oop_share", "Out-of-pocket % health spending", "WB", "%", "lower_better"),
    ("gghe", "Domestic govt health expenditure", "WHO", "% GDP", "higher_better"),
    ("ext_he", "External health expenditure", "WHO", "% CHE", "lower_better"),
    ("medicines", "Essential medicines availability", "WHO", "%", "higher_better"),
]

COVARIATES = [
    ("gdp_pc", "GDP per capita PPP", "WB", "USD", None),
    ("schooling", "Mean years schooling", "WB", "years", None),
    ("urban", "Urbanization rate", "WB", "%", None),
    ("pop_growth", "Population growth rate", "WB", "%", None),
    ("fertility", "Fertility rate", "WB", "births per woman", None),
    ("governance", "Governance effectiveness", "WB", "index", None),
    ("fragility", "Fragile states index", "WB", "index", None),
    ("dah", "Development assistance for health", "IHME", "USD millions", None),
    ("water", "Access to clean water", "WB", "%", None),
    ("sanitation", "Access to sanitation", "WB", "%", None),
    ("fem_edu", "Female secondary education", "WB", "%", None),
    ("conflict", "Conflict intensity score", "WB", "index", None),
    ("internet", "Internet penetration", "WB", "%", None),
    ("agri_emp", "Agricultural employment share", "WB", "%", None),
    ("fdi", "Foreign direct investment", "WB", "% GDP", None),
]

ALL_INDICATORS = (
    COMPREHENSIVE_INDICATORS
    + DISEASE_INDICATORS
    + SYSTEMS_INDICATORS
    + COVARIATES
)

INDICATOR_IDS = [ind[0] for ind in ALL_INDICATORS]
INDICATOR_NAMES = {ind[0]: ind[1] for ind in ALL_INDICATORS}
INDICATOR_SOURCES = {ind[0]: ind[2] for ind in ALL_INDICATORS}

PILOT_DOMAINS = {
    "comprehensive": [ind[0] for ind in COMPREHENSIVE_INDICATORS],
    "disease": [ind[0] for ind in DISEASE_INDICATORS],
    "systems": [ind[0] for ind in SYSTEMS_INDICATORS],
}

# --- Counterfactual intervention grid ---
INTERVENTION_GRID = {
    "che_gdp": [1.0, 3.0, 5.0],
    "physicians": [1.5, 2.0, 3.0],
    "schooling": [1.0, 2.0, 3.0],
    "dtp3": [10.0, 20.0],
    "urban": [5.0, 10.0],
}

# --- WHO/SDG/AU targets for traffic-light evaluation ---
SDG_TARGETS_2030 = {
    "u5_mort": 25.0,
    "neo_mort": 12.0,
    "mat_mort": 70.0,
    "hiv_inc": 0.5,
    "tb_inc": 20.0,
    "mal_inc": 10.0,
    "ncd_mort": 20.0,
    "uhc_index": 80.0,
}
