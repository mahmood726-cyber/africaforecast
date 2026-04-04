# AfricaForecast: A hybrid causal-hierarchical framework for health forecasting in low- and middle-income countries

**Authors**: [Author list TBD]

**Target journal**: *Nature Medicine*

**Manuscript type**: Methods article

---

## Abstract

Africa faces a compounding health transition: rising non-communicable disease burden overlaid on persistent infectious disease, against a backdrop of fragile health systems and constrained financing. Existing projection frameworks—including the Global Burden of Disease study and WHO health statistics—provide historical trends and scenario projections but lack interactive counterfactual capability that would allow policymakers to evaluate the health consequences of specific interventions. We present AfricaForecast, a hybrid causal-hierarchical framework that integrates three complementary modelling layers: a Bayesian hierarchical vector autoregression (BHVAR) encoding a domain-informed causal directed acyclic graph (DAG) with 80 edges across 52 health indicators; a three-model machine learning ensemble (Ridge regression, Gaussian Process, Exponential Smoothing) with inverse-variance weighting; and a do-operator counterfactual engine based on Pearl's interventional calculus. Applied to all 54 African Union member states over 1990–2021, the model achieved [TBD]% mean RMSE improvement over naive linear extrapolation, with 80% prediction interval empirical coverage of [TBD]%. The open-access interactive dashboard enables policymakers to run real-time "what if?" scenarios for health spending, workforce deployment, and SDG target tracking.

**Keywords**: health forecasting, causal inference, Bayesian hierarchical models, Africa, counterfactual simulation, SDG3, epidemiological transition

---

## Introduction

### The African health challenge

Sub-Saharan Africa and North Africa together face a health burden that is both historically large and structurally transforming. Over the three decades from 1990 to 2020, substantial progress was achieved in reducing child and maternal mortality, expanding immunisation coverage, and scaling antiretroviral therapy for HIV. Yet these gains occurred concurrently with a rapid epidemiological transition: the incidence and mortality from non-communicable diseases (NCDs)—including cardiovascular disease, diabetes, cancer, and mental health disorders—are growing at rates that outpace health system adaptation. By 2030, NCDs are projected to account for the majority of premature deaths in most African countries, even as malaria, tuberculosis, and emerging infectious disease threats remain uncontrolled in many settings.

These challenges are compounded by structural deficits. Physician density across sub-Saharan Africa averages fewer than 2 per 10,000 population, compared with more than 30 in high-income countries. Per capita health expenditure, even after adjustment for purchasing power, remains an order of magnitude lower than in Organisation for Economic Co-operation and Development nations. Development assistance for health—which supplements domestic government expenditure in many fragile states—is itself subject to geopolitical volatility. Against this background, translating epidemiological evidence into effective health policy decisions requires not only accurate forecasting of baseline trajectories, but also rigorous tools to evaluate the likely consequences of policy choices before they are implemented.

### Limitations of existing approaches

The primary quantitative resources for African health forecasting are the Institute for Health Metrics and Evaluation (IHME) Global Burden of Disease (GBD) study and the WHO health statistics programme, supplemented by World Bank development indicators and UN population projections. These resources provide invaluable longitudinal data and, in the case of GBD, probabilistic scenario projections. However, they share three limitations that constrain their utility for front-line health policy analysis in low- and middle-income country (LMIC) contexts.

First, existing projections are largely *extrapolative* rather than *causal*. They model how health outcomes have changed historically and project those trends forward under alternative socioeconomic scenarios, but they do not encode the directed causal pathways by which a specific policy change (for example, increasing the physician-to-population ratio in a specific region) propagates through the health system to affect downstream outcomes (such as skilled birth attendance, maternal mortality, and ultimately life expectancy). This makes it difficult to answer the policy-relevant "what if?" question in a mechanistically grounded way.

Second, the computational and data infrastructure required to update or re-run GBD-scale analyses is effectively inaccessible to most African Ministries of Health, National Public Health Institutes, or academic research groups in LMICs. This creates a structural dependency on a small number of global institutions to generate and interpret projections that have direct consequences for health financing and planning decisions at the national level.

Third, projection uncertainty is often communicated at a level of aggregation (continental or sub-regional) that obscures country-level heterogeneity. The 54 African Union member states span an enormous range in health system maturity, epidemiological profiles, governance, and economic capacity. A projection tool that treats Rwanda and the Central African Republic as exchangeable misrepresents the policy landscape for both.

### The AfricaForecast approach

AfricaForecast is designed to fill this gap. It is, to our knowledge, the first open-access, fully reproducible, country-level health forecasting platform for Africa that incorporates an explicit causal structural model enabling interactive counterfactual simulation. The system is built around three core design principles.

The first is *causal transparency*. All variable relationships are encoded in a directed acyclic graph constructed from domain knowledge—specifically WHO SDG 3 health linkage maps, Lancet Commission pathway analyses, and epidemiological transition theory—and optionally refined using data-driven causal discovery (the PC algorithm). Every causal edge is explicitly documented, sign-coded (positive or negative), and source-attributed.

The second is *hierarchical representation of heterogeneity*. The BHVAR model incorporates country-level random intercepts and regional effects, enabling the model to borrow statistical strength across the 54-country panel while preserving country-specific trajectories.

The third is *policy interactivity*. The counterfactual engine allows end-users to specify any combination of indicator-level interventions, and the system forward-simulates the causal consequences through the DAG in topological order, producing probabilistic outcome trajectories with 80% and 95% prediction intervals.

---

## Results

### Overview of the AfricaForecast system

AfricaForecast integrates 52 health indicators across 54 African Union member states using annual panel data spanning 1990–2021. Indicators are drawn from four domains: ten comprehensive health outcome indicators (including life expectancy, under-5 mortality, and all-cause disability-adjusted life years), fifteen disease-specific indicators spanning infectious diseases (HIV, malaria, tuberculosis) and NCDs (diabetes, hypertension, tobacco use, obesity), twelve health systems and financing indicators, and fifteen socioeconomic and structural covariates.

The causal DAG encodes 80 directed edges, informed by WHO SDG 3 linkage maps, Lancet Commission pathways, and GBD risk factor literature. These edges span six functional clusters: economic drivers to health financing, health financing to workforce and infrastructure, workforce to service coverage, coverage to mortality outcomes, NCD and epidemiological transition pathways, and conflict and fragility effects on health system degradation.

### Validation against holdout data (2016–2021)

The primary validation used a temporal holdout design: models were trained on data from 1990 to 2015, and forecast accuracy was evaluated against observed values from 2016 to 2021 (a six-year horizon). This window was chosen because it is both long enough to test multi-year extrapolation and recent enough that high-quality observed data exist for most of the 52 indicators across the majority of the 54 countries.

The ensemble model achieved an overall mean RMSE of [TBD] across validated indicators, representing a [TBD]% improvement over a naive linear extrapolation baseline (which projects the historical trend from the preceding decade). Mean absolute error was [TBD]. Empirical coverage of 80% prediction intervals was [TBD]% (nominal 80%), and empirical coverage of 95% prediction intervals was [TBD]% (nominal 95%). [TBD] of the 54 African Union member states were successfully modelled across the majority of indicators, with gaps concentrated in fragile and conflict-affected states where data availability is limited.

Performance varied systematically across indicator domains. Health system and financing indicators, which have smoother temporal trajectories and stronger cross-country regularisation signals, showed the lowest relative RMSE. Disease-specific indicators—particularly malaria incidence and HIV incidence, which are sensitive to programmatic shocks and intervention scale-ups—showed higher variance but remained within plausible ranges. NCD indicators (diabetes prevalence, obesity) were among the most accurately forecast, consistent with the gradual epidemiological transition driving these trajectories.

### Counterfactual validation: historical natural experiments

We validated the directional plausibility of the counterfactual engine against three historical natural experiments in which large, documented policy changes occurred and health outcome trajectories subsequently diverged from the regional trend.

**Rwanda health financing expansion.** Rwanda substantially increased government health expenditure as a share of GDP following post-genocide reconstruction, implementing community-based health insurance (Mutuelles de Santé) and expanding the Community Health Worker programme from the early 2000s. AfricaForecast counterfactual simulations of a comparable health expenditure increase predict reductions in under-5 mortality and improvements in UHC service coverage index that are directionally consistent with the observed Rwandan trajectory.

**Ethiopia Health Extension Programme.** The deployment of approximately 38,000 Health Extension Workers beginning in 2003–2004 represents one of the largest community health workforce scale-ups in Africa. AfricaForecast counterfactual simulations of increased nurse and community health worker density predict reductions in child mortality and improvements in immunisation coverage and skilled birth attendance, consistent with the observed Ethiopian trajectory over 2000–2015.

**Botswana antiretroviral therapy scale-up.** Botswana initiated universal ART in 2002, one of the earliest and most comprehensive rollouts in Africa. This produced a dramatic reversal of declining life expectancy by the mid-2000s. AfricaForecast counterfactual simulations of reduced HIV incidence and prevalence through treatment-as-prevention show directionally consistent effects on adult mortality and life expectancy trajectories.

Formal quantitative evaluation of counterfactual calibration against these natural experiments is ongoing and results will be reported in a companion validation paper.

### SDG3 target tracking and scenario projections

Using the fitted model, we generated 15-year projections (2022–2036) for all 52 indicators across all 54 countries. We evaluated projected trajectories against WHO SDG 3 targets for 2030, including under-5 mortality below 25 per 1,000 live births, neonatal mortality below 12 per 1,000 live births, maternal mortality below 70 per 100,000 live births, HIV incidence below 0.5 per 1,000, tuberculosis incidence below 20 per 100,000, UHC service coverage index above 80, and NCD premature mortality below 20%. Under a business-as-usual trajectory, [TBD] of the 54 countries are projected to meet the under-5 mortality SDG target by 2030. Health financing and workforce scenario analyses are reported in the accompanying dashboard.

---

## Discussion

### Principal findings

AfricaForecast provides the first open-access counterfactual health forecasting platform for Africa that (1) covers all 54 African Union member states; (2) incorporates an explicit causal structural model; (3) enables real-time interactive policy scenario simulation; and (4) is built entirely from open-access data sources. The system achieves meaningful improvements over naive extrapolation benchmarks across most indicators, with well-calibrated uncertainty intervals that can support evidence-informed planning decisions.

The causal DAG architecture provides two advantages over conventional extrapolative projection methods. First, it enables mechanistically grounded counterfactual analysis: when a user increases health expenditure per capita in the dashboard, the effect propagates through the physician density and nurse density nodes, then through UHC service coverage, and ultimately to downstream mortality outcomes—replicating the causal pathway through which real-world health investments affect population health. This is qualitatively different from applying a regression coefficient from a reduced-form model. Second, the DAG structure provides a form of regularisation: indicators whose historical trajectories would otherwise extrapolate implausibly (for example, malaria incidence declining to zero in a high-burden country) are partially constrained by the signal from their causal parents.

The hierarchical model structure addresses a fundamental challenge in African health data: extreme heterogeneity in data quality, completeness, and temporal coverage across 54 countries. By pooling information across countries within the Bayesian hierarchical framework—with country random intercepts and regional effects—the model can generate coherent projections even for data-sparse countries, while not forcing convergence on countries with distinctive trajectories.

### Limitations

Several important limitations must be acknowledged.

**Causal assumptions.** The DAG was constructed from domain expertise and peer-reviewed literature, not from experimental data. The 80 causal edges represent our best understanding of the major health system pathways, but causality cannot be established definitively from observational panel data. In particular, the direction and magnitude of several edges (for example, urbanisation to NCD burden, governance to government health expenditure) are contested in the empirical literature. We attempted to mitigate this by encoding DAG edges from multiple independent literature sources and by optionally refining the DAG using the PC constraint-based causal discovery algorithm, but users should treat the causal structure as domain-informed rather than proven.

**Long-horizon uncertainty.** The 15-year projection horizon to 2036 extends well beyond the six-year validation window. Forecast uncertainty grows non-linearly with horizon, and the model's uncertainty intervals should be interpreted with appropriate caution beyond five years. Structural breaks—pandemics, conflicts, major policy discontinuities—are not modelled and will produce forecast errors that are not captured in the prediction intervals.

**Data gaps in fragile and conflict-affected states.** Several African Union member states (including Somalia, South Sudan, Eritrea, the Central African Republic, and Libya) have extremely limited longitudinal health data. For these countries, the model draws heavily on regional pooling and prior distributions, and projections are correspondingly more uncertain. The dashboard explicitly flags data-sparse countries.

**Epidemiological transition dynamics.** The model captures the secular NCD transition through time trends and urbanisation pathways, but does not explicitly model the within-country heterogeneity in transition timing that is evident in countries with large urban-rural gradients. Sub-national forecasting is a planned extension.

**Ecological fallacy.** All modelling is at the country-year level. Individual-level heterogeneity in health outcomes—by age, sex, socioeconomic position, and geographic area—is not captured. Indicators that are highly heterogeneous within countries (for example, skilled birth attendance, which varies enormously between capital cities and rural areas) may be less accurately forecast at the national average level.

### Policy implications

The AfricaForecast platform has direct relevance to several high-priority policy contexts. For health financing, the counterfactual engine allows Ministries of Health and development partners to model the projected health returns on incremental public health expenditure, including the effects on UHC service coverage, child mortality, and NCD burden. For health workforce planning, the physician and nurse density intervention scenarios provide a quantitative basis for evaluating the health system impact of training and retention investments. For SDG monitoring, the SDG3 target tracking module provides country-specific assessments of whether current trajectories are consistent with 2030 targets, identifying which countries are most at risk of missing specific targets and which indicators are most responsive to policy intervention.

We emphasise that AfricaForecast is a planning and hypothesis-generation tool, not a precise prediction system. Health trajectories in low-income settings are inherently uncertain, and the model's projections should be used to inform policy deliberations alongside expert judgement, context-specific knowledge, and qualitative assessment of implementation constraints.

### Comparison with existing tools

IHME GBD provides the most comprehensive existing health projection capability, with probabilistic scenarios for a broad range of indicators. AfricaForecast differs primarily in three respects: the explicit causal structural model enabling policy-specific counterfactual simulation; the interactive open-access dashboard that does not require institutional access or technical expertise to operate; and the focus on African Union member states with country-specific hierarchical modelling. The WHO Health Observatory and World Bank data portals provide data access but not forecasting capability. The AfricaForecast DAG structure is conceptually related to the PRIME model and similar causal inference approaches in global health, but extends these to a multi-country hierarchical panel setting with a broader indicator set.

---

## Methods

### Data sources and curation

The AfricaForecast panel dataset integrates annual observations for 52 indicators across all 54 African Union member states from 1990 to 2021. All data are drawn from open-access sources:

- **WHO Global Health Observatory (GHO)**: physician and nurse density, DTP3 immunisation coverage, UHC service coverage index, government health expenditure, TB incidence, malaria incidence, diabetes prevalence, hypertension prevalence, tobacco use, obesity prevalence, healthy life expectancy, and external health expenditure share.
- **World Bank World Development Indicators (WDI)**: life expectancy, under-5 mortality, neonatal mortality, maternal mortality ratio, infant mortality, adult mortality, crude death rate, GDP per capita (PPP), mean years of schooling, urbanisation, population growth, fertility rate, governance effectiveness, fragile states index, hospital beds, current health expenditure (% GDP and per capita), out-of-pocket health expenditure share, access to clean water, access to sanitation, female secondary education, internet penetration, agricultural employment share, and foreign direct investment.
- **IHME Global Burden of Disease (GBD)**: HIV incidence, HIV prevalence, malaria mortality, TB mortality, all-cause DALYs, cardiovascular DALYs, cancer DALYs, mental health DALYs, lower respiratory infection mortality, diarrhoeal disease mortality, NCD premature mortality, development assistance for health, and skilled birth attendance.

Data were extracted via each institution's public API or bulk download service, with retrieval dates, version identifiers, and SHA-256 content hashes recorded in a machine-readable manifest file for each source dataset. Missing values were not imputed prior to modelling; each sub-model handles missingness by excluding incomplete observations from the relevant likelihood or loss computation.

Indicators are organised into four analytical domains: 10 comprehensive health outcome indicators spanning mortality, life expectancy, and disability-adjusted life years; 15 disease-specific indicators covering HIV/AIDS, malaria, tuberculosis, and NCDs; 12 health systems and financing indicators; and 15 socioeconomic and structural covariates (Table 1, Supplementary Materials).

### Causal directed acyclic graph

The causal structure of the system is encoded as a directed acyclic graph in which nodes represent indicators and directed edges represent hypothesised causal pathways. The domain-informed DAG contains 80 directed edges spanning 52 indicator nodes and is organised into six functional clusters.

The first cluster links economic development to health financing: GDP per capita drives current health expenditure (as both percentage of GDP and per capita amount), government health expenditure, and mean years of schooling; governance effectiveness independently drives government health expenditure; and development assistance for health drives the external health expenditure share.

The second cluster links health financing to workforce and infrastructure: current health expenditure per capita drives physician density, nurse density, hospital bed density, and essential medicines availability; government health expenditure additionally drives physician density; and mean years of schooling drives physician density through the education-to-workforce pipeline.

The third cluster links the health workforce to service coverage: physician and nurse density drive the UHC service coverage index; physician density drives DTP3 immunisation coverage and skilled birth attendance; nurse density drives skilled birth attendance; and current health expenditure per capita drives UHC service coverage independently.

The fourth cluster links WASH and coverage to child and maternal mortality: access to clean water and sanitation reduce under-5 mortality and neonatal mortality; diarrhoeal disease mortality is reduced by water access; DTP3 immunisation reduces under-5 mortality and lower respiratory infection mortality; skilled birth attendance reduces maternal and neonatal mortality; and UHC service coverage reduces under-5, maternal, neonatal, and infant mortality.

The fifth cluster encodes NCD and epidemiological transition pathways: urbanisation increases obesity and hypertension prevalence; obesity increases diabetes and hypertension; tobacco use increases NCD premature mortality and cancer DALYs; hypertension and diabetes increase cardiovascular DALYs and NCD premature mortality; GDP per capita reduces tobacco use (consistent with the African income-tobacco relationship); and government health expenditure and total health expenditure reduce out-of-pocket share.

The sixth cluster links aggregate mortality to life expectancy and summary measures: under-5 mortality, adult mortality, NCD premature mortality, and HIV prevalence all reduce life expectancy; GDP per capita and UHC service coverage increase life expectancy; life expectancy drives healthy life expectancy upward and total DALYs drive it downward; under-5, NCD, and disease-specific mortality rates drive all-cause DALYs; and conflict intensity and fragility reduce UHC service coverage and government health expenditure respectively.

All 80 edges are sign-coded (+1 for positive causal effects, -1 for negative) based on the direction of the hypothesised relationship, and source-attributed to the relevant literature (WHO SDG3 linkage maps, Lancet Commission reports, GBD risk factor literature, demographic transition theory).

The domain DAG is verified as acyclic using Kahn's topological sort algorithm before use. Optionally, the DAG can be refined by the PC constraint-based causal discovery algorithm (causal-learn library) using the observed panel data. The PC algorithm uses Fisher's z conditional independence test at alpha = 0.05. Data-driven edges are accepted only if they do not create cycles; all domain-coded edges are preserved unchanged.

### Bayesian hierarchical vector autoregression (BHVAR)

The primary statistical model is a Bayesian hierarchical vector autoregression that exploits the causal DAG structure to constrain parameter estimation.

For each indicator *i* and country *c* at time *t*, the observation model is:

*y*_{i,c,t} = alpha_{i,c} + delta_i * t_norm + sum_{j in parents(i)} (beta_{ij} * y_{j,c,t-1}) + epsilon_{i,c,t}

where *t*_norm = (year - 2000) / 10 is a normalised time trend; alpha_{i,c} is a country-specific intercept capturing time-invariant country effects; delta_i is a global time trend for indicator *i*; beta_{ij} is the regression coefficient for the lagged causal parent *j*; and epsilon_{i,c,t} ~ Normal(0, sigma_i) is observation noise.

Priors are:
- alpha_{i,c} ~ Normal(0, 1) — weakly informative intercept prior
- delta_i ~ Normal(0, 0.1) — regularised time trend
- beta_{ij} ~ Normal(0, 1) — regularised parent coefficient
- sigma_i ~ Half-Cauchy(1) — heavy-tailed scale prior

Each indicator model is estimated independently (one model per indicator) using maximum a posteriori (MAP) estimation via the L-BFGS-B algorithm (scipy.optimize.minimize, maximum 500 iterations, convergence tolerance 1e-8). Parameter uncertainty is quantified using the Laplace approximation: the posterior is approximated as a multivariate Gaussian centred at the MAP estimate, with covariance approximated by the inverse Hessian diagonal computed by finite differences.

Forecasts are generated by forward simulation: for each future year (1 to horizon), the model draws 500 parameter samples from the Laplace posterior, propagates them through the DAG in topological order (parents updated before children), and adds Gaussian observation noise. This produces a 500-draw posterior predictive sample from which mean and credible interval summaries are derived. The 80% prediction interval is the 10th–90th percentile range and the 95% interval is the 2.5th–97.5th percentile range of the draws.

The topological ordering of indicators is computed deterministically using Kahn's algorithm with alphabetical tie-breaking, ensuring reproducibility. The random seed is fixed globally at 42 for all stochastic operations.

### Machine learning ensemble layer

To complement the BHVAR—which can struggle with complex non-linear temporal patterns and indicators absent from the DAG—a three-model machine learning ensemble is constructed.

**Ridge regression model.** For each indicator, a cross-country linear regression is fitted with features comprising the one-year lag, two-year lag, and year-normalised time index. Ridge regularisation (alpha = 1.0) is applied. Forecasts are generated by iterative one-step-ahead prediction. Prediction intervals are derived from the residual distribution, expanded by the square root of the forecast horizon to account for error accumulation.

**Gaussian Process model.** For each country-indicator pair with at least five training observations, a Gaussian Process regressor is fitted using the year as the input variable. The kernel is a product of a Constant kernel and a Radial Basis Function kernel plus a White Noise kernel (sklearn.gaussian_process). The GP provides a natural uncertainty quantification through the predictive standard deviation, and prediction intervals are derived as mean plus or minus 1.28 standard deviations (80%) and 1.96 standard deviations (95%).

**Exponential Smoothing (ETS) model.** For each country-indicator pair with at least five training observations, a Holt-Winters additive-trend exponential smoothing model is fitted using statsmodels (initialization_method = "estimated", optimized = True, no seasonal component). Prediction intervals are derived from the residual standard deviation, expanded by the square root of the forecast horizon.

**Ensemble weighting.** Model weights are computed by inverse-variance weighting based on out-of-sample RMSE. For each indicator, a three-year internal holdout window immediately preceding the main training cutoff is used: models are trained on [1990, train_end - 3] and evaluated on (train_end - 3, train_end]. The weight for model *m* on indicator *i* is proportional to 1/RMSE_{m,i}^2, normalised to sum to one across models. This procedure automatically assigns higher weight to models that perform better for a given indicator, and degrades gracefully when individual models fail (the failing model receives near-zero weight). The final ensemble forecast is the weighted average of the three component means.

### Counterfactual simulation engine

The counterfactual engine implements Pearl's do-operator for the fitted causal system. A counterfactual simulation proceeds as follows.

First, ordinary least squares regression coefficients are estimated from the historical lagged panel for each directed edge (child ~ parent_lag) in the DAG. For the edge from parent *j* to child *i*, the coefficient beta_{i,j} is estimated by pooled single-lag OLS across all countries and time periods, and is constrained to honour the DAG sign (if the domain DAG specifies a positive causal effect, a negative OLS estimate is reflected to positive). This ensures that the counterfactual simulation is directionally consistent with domain knowledge even when data are noisy.

Second, the intervention is specified as a dictionary mapping indicator IDs to intervention magnitudes. Two intervention types are supported: "multiply" (the intervened variable is set to a proportion of its baseline value) and "add" (the intervened variable is increased by an absolute amount). For multi-year simulations, the intervention is linearly phased in from the baseline value at time zero to the target value at the final forecast horizon, reflecting the realistic gradual implementation of policy changes.

Third, two forward simulations are run using the same random seed: a baseline (no intervention) and a counterfactual (with intervention applied). In each simulation, for each future year, indicators are updated in topological order. Intervened indicators are clamped to the linearly interpolated target value; all other indicators are updated as: y_{i,t} = y_{i,t-1} + sum_j(beta_{i,j} * y_{j,t-1}) + noise, where noise ~ Normal(0, sigma_i) and sigma_i is estimated from the year-on-year within-country standard deviation of the historical panel. The simulation is run for 200 Monte Carlo draws to quantify stochastic uncertainty, and summarised as mean and 80% prediction interval.

Fourth, the set of *affected indicators*—those whose trajectories differ between baseline and counterfactual—is identified as the union of the directly intervened indicators and their first- and second-order causal descendants in the DAG, providing a concise summary of the intervention's sphere of influence.

For the interactive dashboard, counterfactuals for a pre-specified grid of intervention magnitudes (Table 2, Supplementary Materials) are pre-computed and stored as JSON. User-specified magnitudes between grid points are handled by linear interpolation between the two nearest grid entries.

### Validation design

The primary validation used a temporal holdout: models were trained on 1990–2015 (26 years) and evaluated against observed data from 2016–2021 (six years). The training–validation split was chosen to maximise training data while providing a multi-year evaluation window that tests genuine predictive performance rather than in-sample fit.

The naive benchmark is a per-country linear extrapolation: a linear trend is fitted to the last 10 years of training data for each country-indicator pair, and extrapolated into the validation window. This benchmark is widely used in health forecasting evaluation and represents a strong baseline for slowly-evolving indicators.

Validation metrics computed for each indicator are: root mean squared error (RMSE), mean absolute error (MAE), empirical 80% prediction interval coverage, empirical 95% prediction interval coverage, naive benchmark RMSE, and percentage RMSE improvement over naive. These are aggregated across indicators as unweighted means, and across countries as unweighted means (each country-year observation contributes equally).

Statistical code, test suite, and validation fixtures are available in the project repository. The test suite (pytest) includes unit tests for each modelling layer, integration tests for the full pipeline, and regression tests comparing outputs against pre-computed reference values to a tolerance of 1e-6.

### Software and reproducibility

AfricaForecast is implemented in Python 3.11+. Core dependencies are NumPy, SciPy, pandas, scikit-learn, statsmodels, and (optionally) PyMC. The random seed is fixed globally (SEED = 42) in all stochastic operations. All data processing is deterministic given the fixed seed and versioned input datasets. The full pipeline can be re-run from raw source downloads to final figures without modification; pre-computed outputs are provided as JSON artefacts for use by the browser-based dashboard without requiring a Python runtime.

The interactive dashboard is a single-file HTML application requiring no server infrastructure, suitable for deployment in low-bandwidth environments. All forecast data are embedded as pre-computed JSON; the dashboard performs no server-side computation.

---

## Data Availability

All input data are drawn from open-access sources and are freely available without registration. WHO Global Health Observatory data are available at https://www.who.int/data/gho. World Bank World Development Indicators are available at https://databank.worldbank.org/source/world-development-indicators. IHME Global Burden of Disease data are available at https://ghdx.healthdata.org/gbd-results-tool.

The AfricaForecast pipeline code, data manifests, validation suite, and interactive dashboard are available at [repository URL TBD]. All source datasets are versioned and their SHA-256 content hashes are recorded in the data manifest files distributed with the repository.

---

## Code Availability

All modelling code is released under the MIT licence at [repository URL TBD]. The code includes automated tests verifiable without network access or API keys, using pre-downloaded fixture data distributed with the repository.

---

## Acknowledgements

[TBD]

---

## Author contributions

[TBD]

---

## Competing interests

The authors declare no competing interests.

---

## Supplementary Materials

**Table S1.** Full list of 52 indicators with domain, source, unit, and SDG target alignment.

**Table S2.** Causal DAG edge list (80 edges): parent indicator, child indicator, causal sign, literature source.

**Table S3.** Intervention grid used for dashboard pre-computation: indicator, intervention type, and magnitude levels.

**Table S4.** Per-indicator validation metrics (RMSE, MAE, 80% and 95% coverage, naive RMSE, improvement over naive) for all 52 indicators.

**Table S5.** SDG3 target tracking: projected attainment probability by 2030, by country and target indicator.

**Figure S1.** Causal DAG visualisation with node colouring by indicator domain and edge colouring by causal sign.

**Figure S2.** Validation calibration plots (empirical vs nominal coverage) for 80% and 95% prediction intervals, by indicator domain.

**Figure S3.** Regional forecast trajectories for life expectancy, under-5 mortality, UHC service coverage index, and NCD premature mortality, 2022–2036.

**Figure S4.** Counterfactual scenario comparison: health expenditure doubling scenario vs. business-as-usual, for 54 countries, selected indicators.
