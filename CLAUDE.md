# AfricaForecast

Causal health forecasting for Africa 2026-2036.

## Quick Start
- `python -m pytest tests/ -v` to run tests
- `python engine/run_pipeline.py` to run full pipeline
- Open `dashboard/africa_forecast.html` in browser

## Rules
- All data OA-only (WHO GHO, World Bank WDI, IHME GBD, UN WPP)
- Never store API keys or credentials
- Fixed seeds everywhere (SEED = 42)
- Pre-compute all forecasts; dashboard is read-only JSON consumer
- localStorage prefix: `af_`
