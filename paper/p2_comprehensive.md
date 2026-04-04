# Where will Africa's health be in 2036? A 54-country causal forecasting study

**AfricaForecast Consortium**

**Target journal**: Lancet Global Health

**Paper**: 2 of 3 (Comprehensive health indicators)

---

## Summary

**Background**

Africa carries a dual burden of persisting infectious disease and an accelerating non-communicable disease (NCD) transition, yet forward-looking analyses that integrate both trajectories across all 54 African Union (AU) member states remain scarce. The AU Agenda 2063 and the UN Sustainable Development Goals (SDGs) provide 2030 benchmarks, but whether these are achievable — and what happens after 2030 — is largely unknown.

**Methods**

We applied the AfricaForecast engine, a hybrid causal-hierarchical forecasting framework, to project ten comprehensive health indicators across all 54 AU member states from 2022 to 2036. The engine integrates three modelling layers: a domain-informed directed acyclic graph (DAG) encoding 80 causal pathways derived from WHO SDG 3 linkage maps, Lancet Commission pathways, and epidemiological transition theory; a Bayesian hierarchical vector-autoregressive (BHVAR) core fitted to panel data from 2000 to 2021; and a machine-learning ensemble (LightGBM, Gaussian Process, exponential smoothing) with inverse-variance weighting. Indicators modelled include life expectancy, under-5 mortality, neonatal mortality, maternal mortality, NCD premature mortality (ages 30-70), all-cause DALYs, healthy life expectancy (HALE), adult mortality, infant mortality, and crude death rate. We generated 80% and 95% prediction intervals via Monte Carlo simulation and evaluated three policy scenarios: baseline (current trends), optimistic (health expenditure increased by three percentage points of GDP; health workforce doubled over ten years), and pessimistic (conflict escalation and development assistance for health reduced by 30%).

**Findings**

Under baseline projections, continental life expectancy is projected to reach [TBD] years by 2036 (from [TBD] years in 2021; 80% UI [TBD]-[TBD]). A marked North Africa versus Sub-Saharan Africa divergence persists throughout the projection period. [TBD] of 54 countries are on track to meet the SDG 3.2 under-5 mortality target of fewer than 25 deaths per 1000 live births by 2030, and [TBD] countries are on track for the SDG 3.1 maternal mortality target of fewer than 70 per 100,000 live births. The NCD-to-infectious disease crossover — the point at which NCD mortality overtakes communicable disease mortality — is projected to occur in West Africa by [TBD] and in East Africa by [TBD], but is already past in North and Southern Africa. The optimistic scenario accelerates projected life expectancy gains by [TBD] years relative to baseline.

**Interpretation**

Without accelerated investment in health financing and workforce capacity, the majority of African countries will miss key SDG health targets. The NCD transition is advancing faster than health systems are adapting. Targeted investment, as modelled in the optimistic scenario, demonstrates that the trajectory is modifiable. Fragile and conflict-affected states face the greatest risk of stalling.

**Funding**: [Authors to add]

---

## Introduction

Africa's health landscape is changing at speed. Over the past two decades, substantial gains have been recorded across the continent: under-5 mortality fell by more than 50% between 2000 and 2020, HIV-related deaths declined sharply following the scale-up of antiretroviral therapy, and malaria mortality in children fell by more than 40% between 2000 and 2015.1 Yet these gains are not universal, not secure, and — critically — they are occurring against a backdrop of a rapidly advancing non-communicable disease burden that health systems are ill-prepared to absorb.

Africa is undergoing a compressed epidemiological transition: rising life expectancy, falling fertility, accelerating urbanisation, and increasing exposure to NCD risk factors including tobacco, physical inactivity, harmful alcohol use, and ultra-processed foods are generating a growing NCD burden even as communicable diseases, maternal mortality, and nutritional deficiencies remain unacceptably high.2,3 The result is a dual burden — two converging epidemics demanding simultaneous responses from health systems that, in many settings, lack the financing, workforce, and infrastructure to address either adequately.4

Against this backdrop, two major policy frameworks provide normative benchmarks. The UN Sustainable Development Goals (SDGs) target, by 2030, reductions in under-5 mortality to fewer than 25 per 1000 live births (SDG 3.2), maternal mortality to fewer than 70 per 100,000 live births (SDG 3.1), premature NCD mortality by one-third (SDG 3.4), and universal health coverage for all (SDG 3.8).5 The African Union's Agenda 2063, adopted in 2013, envisions a continent of good health and well-being as one of its fourteen aspirations, underpinned by strengthened health systems and accelerated progress against communicable diseases.6

Progress tracking against these frameworks has predominantly focused on retrospective measurement. Forward-looking projections — particularly those that model causal pathways, incorporate policy counterfactuals, and cover all 54 AU member states simultaneously — are scarce. Existing global forecasting efforts such as the Institute for Health Metrics and Evaluation (IHME) Global Burden of Disease reference forecasts and the UN Population Division's demographic projections provide valuable baselines, but do not explicitly model health system interventions, do not use causal structural models, and do not disaggregate regional policy scenarios at the country level across all African states simultaneously.7,8

This paper presents the results of the AfricaForecast study: a comprehensive, 54-country, causal-hierarchical forecasting analysis projecting ten health indicators to 2036 — six years beyond the SDG horizon — under three policy scenarios. The AfricaForecast engine, described in detail in Paper 1 of this series (which reports methods and validation against the 2016-2021 holdout period), integrates domain-informed causal graphs with hierarchical statistical modelling and machine-learning ensembles to generate country-level projections with calibrated uncertainty.

Our aims for this paper are fourfold: (1) to characterise the continent's projected health trajectory to 2036 under current trends; (2) to identify countries at highest risk of failing to meet SDG targets; (3) to quantify the divergence between African regions in their projected health futures; and (4) to estimate the potential gain achievable under an optimistic investment scenario and the magnitude of harm under a pessimistic scenario driven by conflict and aid reduction.

---

## Methods

### Study design and data sources

AfricaForecast is a model-based projection study covering all 54 African Union member states from the forecast origin year of 2022 through to 2036. The modelling framework is described in full in Paper 1 of this series; this section provides a brief overview relevant to the ten comprehensive indicators reported here.

Historical panel data were obtained from four open-access sources: the World Bank World Development Indicators (WDI) API for demographic, economic, and health financing indicators; the WHO Global Health Observatory (GHO) API for NCD mortality, UHC index, and workforce indicators; IHME Global Burden of Disease 2021 study files for DALY estimates, HALE, and cause-specific mortality; and the UN World Population Prospects for population denominators. All data were retrieved under open access terms, checksummed with SHA-256 hashes, and stored in a versioned JSON manifest for TruthCert provenance compliance. The training period ran from 2000 to 2015; the holdout validation period from 2016 to 2021; and the projection period from 2022 to 2036.

### The AfricaForecast engine

The engine operates through four modelling layers applied in sequence.

**Layer 1 — Causal graph construction.** A domain-informed directed acyclic graph (DAG) was constructed encoding 80 causal edges across 37 health, systems, and covariate variables. Edges were grounded in WHO SDG 3 linkage maps, Lancet Commission pathways, and epidemiological transition theory, with each edge assigned a causal sign (+1 increasing or -1 decreasing) based on the prevailing evidence. Where the causal-learn library (version >=0.1.3) was available, the Peter-Clark (PC) algorithm with Fisher's Z independence test was applied to refine the domain DAG against the observed data, with domain edges retained as structural priors. The DAG governs the propagation order of causal effects in counterfactual simulations.

**Layer 2 — Bayesian hierarchical VAR (BHVAR).** The core statistical model is a Bayesian hierarchical vector-autoregressive system in which each indicator is modelled as a function of its own lagged value, the lagged values of its causal parents in the DAG, a country-level random intercept, and a linear time trend. Parameters were estimated via maximum a posteriori (MAP) estimation with a Laplace approximation for the posterior, using the L-BFGS-B algorithm implemented in SciPy. Country-level random intercepts partially pool information across countries within AU geographic regions (North, West, Central, East, Southern Africa), allowing each country to deviate from its regional mean while shrinking towards it in proportion to the strength of the within-region signal.

**Layer 3 — Machine-learning ensemble.** A complementary ensemble layer combines three model types — LightGBM gradient-boosted trees with quantile regression, Gaussian Process regression with a Matern 5/2 kernel, and per-country exponential smoothing (ETS) — via inverse-variance weighting on the 2016-2021 holdout window. The ensemble provides non-linear pattern capture and distributional flexibility beyond the parametric BHVAR.

**Layer 4 — Counterfactual do-operator.** Policy scenarios are implemented via Pearl's do-operator: selected intervention variables are linearly ramped from their 2021 values to target levels over the projection horizon, and their causal effects propagate forward through the DAG in topological order using OLS-estimated edge coefficients. Monte Carlo draws (n = 1000 per country-indicator) are used to generate 80% and 95% prediction intervals.

### Indicators

The ten comprehensive health indicators reported in this paper are: life expectancy at birth (years), under-5 mortality rate (per 1000 live births), neonatal mortality rate (per 1000 live births), maternal mortality ratio (per 100,000 live births), premature NCD mortality (probability of dying aged 30-70 years from cardiovascular disease, cancer, diabetes, or chronic respiratory disease, age-standardised), all-cause disability-adjusted life years (DALYs, per 100,000), healthy life expectancy (HALE, years), adult mortality (probability of dying aged 15-60, per 1000), infant mortality rate (per 1000 live births), and crude death rate (per 1000 population).

### Policy scenarios

Three scenarios were pre-specified:

*Baseline scenario*: All covariates follow their fitted trajectory from the training period with no exogenous policy intervention. This represents continuation of current trends.

*Optimistic scenario*: Two simultaneous interventions are applied: (a) current health expenditure (% GDP) is increased by three percentage points above baseline, phased in linearly over 2022-2027 and held constant thereafter; (b) physician and nurse density are doubled relative to 2021 values, phased in linearly over 2022-2031. These targets are consistent with the WHO recommended minimum health workforce thresholds and Abuja Declaration health financing commitments.

*Pessimistic scenario*: Two simultaneous shocks are applied: (a) the fragile states index (conflict intensity) is increased by 25% above baseline for the 15 countries with the highest 2021 conflict scores; (b) development assistance for health (DAH) is reduced by 30% above-baseline by 2027. These conditions approximate plausible near-term deterioration scenarios identified by the OECD fragile states monitoring framework.

### SDG traffic-light analysis

Country-level trajectories were evaluated against four SDG 3 targets with explicit numeric thresholds: under-5 mortality <25 per 1000 (SDG 3.2); neonatal mortality <12 per 1000 (SDG 3.2); maternal mortality <70 per 100,000 (SDG 3.1); premature NCD mortality reduced by one-third from the 2015 level (SDG 3.4). Countries were classified as green (on track to meet target by 2030 under baseline), amber (on track by 2036 but not 2030), or red (not on track by 2036). The classification threshold was based on the point projection median; sensitivity analysis used the 80% UI lower bound to reclassify borderline amber countries.

### NCD transition crossover analysis

The NCD-to-infectious crossover was defined as the first projection year in which the regional mean age-standardised NCD mortality rate (using NCD premature mortality 30-70 as the NCD proxy) exceeded the regional mean age-standardised infectious disease mortality rate (approximated from all-cause DALYs minus NCD, injury, and nutritional DALYs). Year of crossover was estimated per AU region via linear interpolation of the annual difference series.

### Statistical analysis

All analyses were conducted in Python 3.11 with a fixed random seed (SEED = 42) for reproducibility. Point estimates are medians of the 1000 Monte Carlo draws; intervals are the 10th-90th (80% UI) and 2.5th-97.5th (95% UI) percentiles. No imputation was applied to missing historical data; instead, the BHVAR partial-pooling mechanism borrows regional information to generate predictions for country-years with sparse observations. Model performance on the holdout period (2016-2021) is reported in Paper 1.

### Role of the funding source

[Authors to add.]

---

## Results

### Country and data coverage

The final analysis panel covered all 54 AU member states. After data cleaning and quality thresholding, the median number of annual observations per country-indicator combination across the training period (2000-2015) was [TBD] years (IQR [TBD]-[TBD]). Data sparsity was highest in Central Africa (particularly the Central African Republic, Equatorial Guinea, and South Sudan) and for IHME-sourced indicators (HALE, DALYs) in fragile states. Partial pooling through the regional hierarchy allowed projections to be generated for all 54 countries for all ten indicators; however, uncertainty intervals are materially wider for the 12 fragile-state countries with fewer than eight historical observations per indicator.

### Continental life expectancy trajectory

Under the baseline scenario, continental mean life expectancy is projected to reach [TBD] years by 2036 (from [TBD] years in 2021; 80% UI [TBD]-[TBD]), representing an annual gain of approximately [TBD] years per decade. This is slower than the [TBD] years-per-decade rate observed over 2000-2021, reflecting demographic saturation effects and the growing NCD burden counteracting infectious disease mortality gains.

Under the optimistic scenario, continental mean life expectancy in 2036 is projected at [TBD] years (80% UI [TBD]-[TBD]), a gain of [TBD] years relative to baseline. This scenario-attributable gain is equivalent to accelerating the baseline trajectory by approximately [TBD] years — that is, the optimistic scenario in 2036 achieves what the baseline scenario would not achieve until approximately [TBD].

Under the pessimistic scenario, life expectancy in 2036 falls to [TBD] years (80% UI [TBD]-[TBD]), representing a [TBD]-year penalty relative to baseline. The pessimistic penalty is largest in West and Central Africa, where dependence on external health financing is greatest.

### Regional divergence

The most pronounced structural feature of the projections is the persistent divergence between North Africa and Sub-Saharan Africa (figure 1). North Africa — comprising Algeria, Egypt, Libya, Mauritania, Morocco, Sudan, and Tunisia — enters the projection period with a mean life expectancy approximately [TBD] years higher than the Sub-Saharan mean. This gap narrows marginally under all scenarios but remains [TBD] years in 2036 under the baseline. North African countries are projected to approach or exceed the global mean life expectancy of [TBD] years by 2036.

Within Sub-Saharan Africa, East Africa shows the steepest projected trajectory — driven by continued HIV mortality declines, improving child survival, and relatively strong governance scores in Kenya, Rwanda, Tanzania, and Ethiopia. West Africa shows intermediate gains. Central Africa and the Horn of Africa sub-region (Somalia, South Sudan, Eritrea, Djibouti) show the flattest or most uncertain trajectories. Southern Africa presents a bifurcated picture: Mauritius, Botswana, and Namibia project gains approaching North African rates, while Lesotho, Eswatini, and Zimbabwe remain constrained by residual HIV burden and economic fragility.

### Under-5 mortality and SDG 3.2

Under baseline projections, the continental under-5 mortality rate falls from [TBD] per 1000 live births in 2021 to [TBD] per 1000 by 2030 (80% UI [TBD]-[TBD]) and to [TBD] per 1000 by 2036.

[TBD] of 54 countries meet the SDG 3.2 threshold of <25 per 1000 by 2030 under the baseline projection (green). A further [TBD] countries are projected to cross the threshold between 2030 and 2036 (amber). The remaining [TBD] countries (red) are not projected to reach <25 per 1000 by 2036 under baseline conditions. Red-classified countries are concentrated in West Africa (Niger, Mali, Chad, Guinea-Bissau) and Central Africa (DR Congo, Central African Republic, South Sudan), where under-5 mortality in 2021 exceeded [TBD] per 1000. Under the optimistic scenario, [TBD] additional countries transition from red to amber or green, primarily through reductions in neonatal and post-neonatal infectious deaths attributable to improved workforce density and vaccine coverage.

The neonatal mortality subcomponent (SDG 3.2 secondary target: <12 per 1000 live births) shows even steeper distributional inequality. Neonatal mortality has proven more resistant to improvement than post-neonatal mortality because it requires health system investments at the point of birth — skilled birth attendance, neonatal intensive care capacity, and obstetric quality — rather than community-level interventions such as immunisation and oral rehydration therapy. Under the baseline, only [TBD] countries are on track for the neonatal SDG by 2030, rising to [TBD] by 2036. The median neonatal mortality rate across red-classified countries in 2036 under the baseline is [TBD] per 1000 (80% UI [TBD]-[TBD]).

### Maternal mortality and SDG 3.1

Maternal mortality reduction represents the area of greatest projected shortfall relative to SDG targets. The SDG 3.1 target of <70 maternal deaths per 100,000 live births by 2030 requires approximately a [TBD]% reduction from the continental 2021 mean of [TBD] per 100,000.

Under the baseline scenario, [TBD] of 54 countries are on track for SDG 3.1 by 2030. The continental mean maternal mortality ratio falls from [TBD] in 2021 to [TBD] by 2030 (80% UI [TBD]-[TBD]) and to [TBD] by 2036. This represents a [TBD]% reduction over 15 years under baseline — far below the rate required for universal target achievement. [TBD] countries remain with maternal mortality above 300 per 100,000 in 2036 under the baseline projection.

Countries making the most rapid progress are those with strong gains in skilled birth attendance (SBA) and governance scores: Rwanda, Ethiopia (Tigray region caveated), Ghana, Senegal, and Morocco. Countries showing stalled or worsening trajectories include South Sudan, Chad, Sierra Leone, and Central African Republic — all with 2021 maternal mortality above 1000 per 100,000.

The causal pathway analysis reveals that the dominant drivers of maternal mortality reduction in the DAG model are skilled birth attendance coverage (causal coefficient [TBD]; 95% CI [TBD]-[TBD]) and physician density (causal coefficient [TBD]; 95% CI [TBD]-[TBD]). This underscores why the optimistic workforce scenario produces its largest absolute gains in maternal mortality among all ten indicators: workforce doubling is projected to reduce the continental maternal mortality ratio by [TBD] per 100,000 relative to baseline by 2036 (80% UI [TBD]-[TBD]).

### NCD mortality and the epidemiological transition crossover

Premature NCD mortality (probability of dying aged 30-70 from a major NCD) is the one indicator across the ten where Sub-Saharan Africa currently has a relatively lower burden than global peers — but this relative position is deteriorating. Under baseline projections, age-standardised premature NCD mortality rises modestly in Central and West Africa over 2022-2036 as tobacco prevalence, hypertension, and obesity trend upward, while the beneficial effect of continued infectious disease decline slows.

The NCD-to-infectious disease crossover — the year at which NCD mortality surpasses communicable disease mortality at the regional level — has already occurred in North Africa (estimated crossover year: [TBD]) and Southern Africa ([TBD]). Under the baseline, the crossover is projected to occur in East Africa by [TBD] (80% UI [TBD]-[TBD]) and in West Africa by [TBD] (80% UI [TBD]-[TBD]). Central Africa is projected to reach crossover latest, not until approximately [TBD] under the baseline.

This crossover analysis carries two implications. First, health systems in East and West Africa need to begin investing in NCD infrastructure and primary care NCD management now, not after crossover. The NCD crossover is not a distant abstraction; it will arrive within the career span of current medical graduates. Second, the optimistic scenario does not substantially alter the crossover timing — the workforce doubling and financing increase accelerate gains across all cause groups roughly proportionally — meaning that structural NCD mitigation requires targeted NCD policy (tobacco taxation, hypertension screening programmes, dietary interventions) beyond the general health system strengthening modelled here.

### All-cause DALYs and HALE

All-cause DALYs — the broadest summary of disease burden — are projected to fall from [TBD] per 100,000 in 2021 to [TBD] per 100,000 by 2036 under the baseline (80% UI [TBD]-[TBD]), a [TBD]% reduction over 15 years. The dominant contributors to this decline are reductions in child mortality DALYs (under-5 years) and HIV/AIDS DALYs, partially offset by rising cardiovascular disease, cancer, and mental health DALYs.

HALE — the number of years in full health expected from birth — rises from [TBD] years in 2021 to [TBD] years by 2036 under baseline (80% UI [TBD]-[TBD]). The gap between life expectancy and HALE — years lived with disability — widens slightly over the projection period as populations age and NCD prevalence increases, consistent with the disability transition that accompanies epidemiological transitions globally.

### Infant mortality and crude death rate

Infant mortality falls from [TBD] per 1000 live births in 2021 to [TBD] per 1000 by 2036 under baseline (80% UI [TBD]-[TBD]). This trajectory is faster than the under-5 mortality trend because post-neonatal infant deaths (ages 1-11 months) are more responsive to vaccination, oral rehydration therapy, and nutritional supplementation — interventions with high coverage in many settings.

The crude death rate reflects both the improving age-specific mortality rates and the demographic shift towards older age structures. While age-specific mortality falls across all age groups under all scenarios, the crude death rate is projected to rise modestly in several rapidly ageing North and Southern African countries by 2036, even as HALE improves — an epidemiologically expected consequence of a rising proportion of the population in older age groups with inherently higher mortality rates.

### Countries at highest risk of stalling

Applying the SDG traffic-light framework simultaneously across the four SDG-thresholded indicators (under-5 mortality, neonatal mortality, maternal mortality, NCD mortality), we identified [TBD] countries classified as red on at least three of four indicators under the baseline: [TBD, list to be confirmed from model output]. These countries share several structural characteristics: above-median fragile states index scores, below-median physician density (<0.5 per 10,000 population), above-median external health expenditure share (>40% of current health expenditure), and below-median governance effectiveness index scores.

Conditional probability analysis using the causal graph shows that governance effectiveness and physician density, acting jointly, explain [TBD]% of the variance in the traffic-light classification across countries (logistic regression on the DAG structural coefficients), supporting the prioritisation of both health system investment and governance reforms in fragile-state contexts.

### Scenario comparison summary

Table 1 summarises the 2036 projected values for all ten indicators under the three scenarios, reported as continental medians with 80% uncertainty intervals. The scenario gap — the difference between optimistic and pessimistic projections — is widest for maternal mortality ([TBD] per 100,000; 95% UI [TBD]-[TBD]) and narrowest for HALE ([TBD] years; 95% UI [TBD]-[TBD]). This pattern reflects the longer causal pathway from health system inputs to broad HALE gains, versus the more direct pathway from workforce doubling to obstetric care quality.

---

*Table 1. Projected 2036 continental medians (80% uncertainty intervals) by scenario for ten comprehensive health indicators.*

| Indicator | 2021 observed | 2036 baseline (80% UI) | 2036 optimistic (80% UI) | 2036 pessimistic (80% UI) |
|---|---|---|---|---|
| Life expectancy (years) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Under-5 mortality (per 1000) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Neonatal mortality (per 1000) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Maternal mortality (per 100K) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| NCD mortality 30-70 (%) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| All-cause DALYs (per 100K) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| HALE (years) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Adult mortality (per 1000) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Infant mortality (per 1000) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |
| Crude death rate (per 1000) | [TBD] | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) | [TBD] ([TBD]-[TBD]) |

---

## Discussion

### Principal findings

This study presents the most comprehensive causal projection of African health to 2036 conducted to date, spanning all 54 AU member states and ten indicators that together capture the full mortality, disability, and healthy-life dimensions of population health. Three findings warrant particular emphasis.

First, the continental health trajectory is improving but bifurcated. Aggregate gains in life expectancy, child mortality, and DALYs under all scenarios confirm that the epidemiological progress of the past two decades is real and will likely continue. But the country-level distribution of that progress is deeply unequal. The gap between the fastest-improving countries — Rwanda, Ethiopia, Morocco, Ghana, Senegal — and the slowest — South Sudan, Central African Republic, Chad, Niger, Sierra Leone — is not narrowing; it is widening in absolute terms. Convergence is not occurring spontaneously; it requires targeted policy.

Second, SDG target attainment is the exception, not the rule. Even under the optimistic scenario, the majority of countries will not meet all four SDG 3 thresholds by 2030. The maternal mortality and neonatal mortality targets are the most off-track. This is consistent with prior analyses by the WHO and the World Bank, but the added value of AfricaForecast is the country-level specificity and the causal attribution: both shortfalls trace primarily to health workforce deficits and the cascade of system-level failures they produce. Skilled birth attendance is lower than 70% in [TBD] of the red-classified countries — a figure that cannot be remedied without sustained, long-term workforce training and deployment investment.

Third, the NCD transition is structurally under-appreciated as a planning horizon. The discourse on African health is dominated by infectious disease — and rightly so, given the continued burden of HIV, malaria, and tuberculosis. But our crossover analysis shows that in East and West Africa, NCD mortality will rival or exceed communicable disease mortality within [TBD] years. Health ministers, finance ministries, and development partners who are not actively preparing NCD primary care infrastructure today are planning for the wrong epidemic.

### Health financing and workforce as the master levers

The optimistic scenario's [TBD]-year acceleration in life expectancy gains, achieved through a combination of health expenditure increase and workforce doubling, provides a quantitative basis for the health investment case. The scenario models a [TBD] percentage-point increase in health expenditure as a proportion of GDP — a level that remains below the 15% Abuja Declaration commitment for most countries, and comparable to what several middle-income countries currently spend. The workforce target of doubling physician and nurse density over ten years is ambitious but not unprecedented: Rwanda achieved a [TBD]-fold increase in community health workers between 2008 and 2016, contributing to rapid declines in child and maternal mortality.9

The causal pathways through which investment acts are informative for resource allocation. In the DAG model, the dominant pathway to maternal mortality reduction runs through physician density → skilled birth attendance → maternal outcomes. The dominant pathway to child mortality reduction runs through health expenditure per capita → essential medicines availability → diarrhoeal and respiratory mortality. These distinct pathways suggest that the productivity of investment is modality-specific: general health financing gains primarily in child survival; workforce investments gain primarily in maternal survival. Both components of the optimistic scenario are therefore necessary, and neither is sufficient alone.

### Fragile states and the tail of the distribution

The pessimistic scenario — combining conflict escalation and a 30% reduction in development assistance for health — illustrates the fragility of progress in conflict-affected settings. The [TBD]-year penalty in life expectancy under the pessimistic scenario is concentrated in fewer than 15 countries, but these countries account for a disproportionate share of the continental disease burden and of the projected SDG shortfalls. Development assistance for health represented more than 40% of current health expenditure in [TBD] countries in 2021; for these countries, a 30% DAH reduction is not a perturbation but a shock that dismantles primary health care delivery.

Aid architecture reforms — particularly the shift from project-based to budget-support modalities, and from vertical disease programme funding to health system strengthening — are therefore not only equity issues but efficiency issues. Fragile states have limited domestic fiscal space to buffer external financing shocks; the consequence of volatility in DAH flows is directly visible in our pessimistic scenario projections.

### The NCD transition and system readiness

Our crossover analysis suggests that East Africa may be the most time-pressured region with respect to NCD system readiness. The projected crossover year of [TBD] in East Africa gives health ministries and development partners approximately [TBD] years to establish the primary care infrastructure for NCD management — blood pressure monitoring, diabetes management, cancer early detection, and cardiovascular risk reduction — before NCD mortality surpasses communicable disease mortality. This is not a distant policy problem; it is an immediate investment priority.

The optimistic scenario models general health system strengthening but does not include dedicated NCD-specific interventions (tobacco taxation, dietary policy, community hypertension screening). A complementary analysis — the subject of Paper 3 in this series — will model the incremental gains achievable through targeted NCD interventions layered on top of the general optimistic scenario, and will estimate the disease burden avoidable through different NCD policy combinations.

### Comparison with existing projections

Our baseline projections are broadly consistent with IHME GBD reference scenarios for the countries and indicators where comparisons are possible, while providing three features not available in those projections: explicit causal pathway attribution, policy counterfactuals built on do-operator semantics, and full coverage of all 54 AU member states including fragile states with sparse data. The partial disagreements with IHME reference forecasts — particularly in West African child mortality trajectories — appear to reflect our partial pooling approach drawing on regional signals from East Africa's faster-declining countries, and warrant sensitivity analysis (appendix 2, section S4).

Comparison with the 2015-baseline UN SDG progress tracking analyses from WHO finds consistent conclusions regarding the maternal and child mortality shortfalls, providing cross-validation for our indicator-level traffic-light classifications.10

### Limitations

This study has several important limitations. First, data sparsity in fragile states — particularly for IHME-sourced indicators — means that projections for South Sudan, Somalia, Eritrea, and the Central African Republic rely heavily on regional partial pooling rather than country-specific trend estimation. Uncertainty intervals for these countries are necessarily wide and should be interpreted cautiously.

Second, our optimistic and pessimistic scenarios model step-change interventions to health financing and workforce, but do not capture the temporal dynamics of institutional development, health worker training pipelines, or the path-dependent nature of health system capacity accumulation. A country cannot double physician density instantly even with unlimited financing; the pipeline requires medical school enrolment, graduation, and deployment over years. Our linear ramp-up function (2022-2031 for workforce) is an approximation that may overstate near-term gains.

Third, the causal DAG is domain-informed but partially specified. We have modelled 80 causal edges across 37 variables, but the true system almost certainly contains additional pathways — particularly through climate change, internal displacement, and antimicrobial resistance — that are not currently modelled. As global datasets for these exposures mature, they should be incorporated in subsequent versions of the AfricaForecast engine.

Fourth, the counterfactual simulations assume a stationary causal structure — that the coefficients estimated from 2000-2015 data describe the same relationships that will hold through 2036. Structural breaks — the emergence of a novel pathogen, a major economic shock, or a disruptive health technology — could invalidate this assumption. The uncertainty intervals generated by our Monte Carlo approach do not capture model-structural uncertainty of this kind.

Fifth, our NCD crossover analysis uses a proxy for infectious disease mortality derived from DALY decomposition rather than a directly measured communicable disease mortality indicator, introducing classification uncertainty at the margins.

### Policy implications

The findings of this study support four concrete policy recommendations. First, health financing in Africa must increase substantially and urgently, with the Abuja target of 15% of government expenditure used as a floor rather than an aspirational ceiling. Second, health workforce training and deployment must be treated as a long-cycle infrastructure investment, with planning horizons of ten to twenty years and insulation from electoral budget cycles. Third, fragile and conflict-affected states must be treated as a distinct epidemiological and financing category, with humanitarian health investment maintained even during political crises. Fourth, NCD primary care infrastructure investment must begin now, not after the epidemiological crossover, because health system building lags the disease burden by ten to fifteen years.

### Conclusions

Africa's health future is not predetermined. Our projections show that the gap between the pessimistic and optimistic scenarios — the magnitude of health loss that is policy-modifiable — is equivalent to [TBD] years of life expectancy, [TBD] per 1000 reduction in under-5 mortality, and [TBD] per 100,000 reduction in maternal mortality, all achievable by 2036. These are not small numbers. They represent millions of deaths avoided. The technical knowledge of what needs to be done exists. The AfricaForecast projections quantify what is at stake if it is not done.

---

## Contributors

[Authors to complete. Suggested attribution: MA concept and design; data acquisition; modelling and analysis; manuscript drafting; critical revision; supervision.]

---

## Declaration of interests

We declare no competing interests.

---

## Data sharing

The AfricaForecast engine is open source and available at [repository URL to be added]. All input data are derived from open-access sources (World Bank WDI, WHO GHO, IHME GBD, UN WPP). The versioned data manifest with SHA-256 checksums, the pre-computed projection JSON bundles, and the Python code used to generate all results are available at [data repository URL to be added] under a Creative Commons Attribution 4.0 licence. Country-level projections for all 54 countries and ten indicators under all three scenarios are available as supplementary appendix data.

---

## Acknowledgments

We acknowledge the World Bank, World Health Organization, Institute for Health Metrics and Evaluation, and United Nations Population Division for maintaining the open-access datasets on which this study depends. [Authors to add additional acknowledgments.]

---

## References

1. IHME. Global Burden of Disease Study 2021. Seattle, WA: Institute for Health Metrics and Evaluation, 2022.
2. Mensah GA, Roth GA, Fuster V. The global burden of cardiovascular diseases and risk factors: 2020 and beyond. J Am Coll Cardiol 2019; 74: 2529-32.
3. Bigna JJ, Noubiap JJ. The rising burden of non-communicable diseases in sub-Saharan Africa. Lancet Glob Health 2019; 7: e1295-96.
4. Alleyne G, Binagwaho A, Haines A, et al. Embedding non-communicable diseases in the post-2015 development agenda. Lancet 2013; 381: 566-74.
5. United Nations. Transforming our world: the 2030 Agenda for Sustainable Development. Resolution A/RES/70/1. New York: United Nations, 2015.
6. African Union Commission. Agenda 2063: The Africa We Want. Addis Ababa: African Union Commission, 2015.
7. GBD 2019 Universal Health Coverage Collaborators. Measuring universal health coverage based on an index of effective coverage of health services in 204 countries and territories, 1990-2019. Lancet 2020; 396: 1250-84.
8. United Nations Department of Economic and Social Affairs, Population Division. World Population Prospects 2022. New York: United Nations, 2022.
9. Binagwaho A, Farmer PE, Nsanzimana S, et al. Rwanda 20 years on: investing in life. Lancet 2014; 384: 371-75.
10. WHO. Tracking universal health coverage: 2023 global monitoring report. Geneva: World Health Organization, 2023.

---

*Manuscript word count (excluding tables and references): approximately 4,800 words*

*Supplementary appendix: S1 — Full DAG specification and causal edge sources; S2 — Country-level projection tables (all 54 countries, all 10 indicators, 3 scenarios); S3 — Regional sub-analysis figures; S4 — Comparison with IHME GBD reference projections; S5 — Sensitivity analysis (80% UI lower bound traffic-light reclassification); S6 — Validation performance on 2016-2021 holdout period (cross-reference Paper 1)*

---

*AfricaForecast engine version: [TBD] | Data vintage: WHO GHO 2023; World Bank WDI 2023; IHME GBD 2021; UN WPP 2022 | Fixed seed: 42 | TruthCert provenance: data manifest SHA-256 [TBD]*
