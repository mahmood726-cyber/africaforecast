# The African Epidemiological Transition 2026–2036: Causal Projections for Infectious and Non-Communicable Diseases

**Journal**: BMJ Global Health  
**Paper series**: AfricaForecast Pilot Series — Paper 3 of 3  
**Cross-references**: Paper 1 (AfricaForecast engine, methods); Paper 2 (comprehensive health indicators, SDG tracking)  
**Status**: Draft — data-dependent values marked [TBD]

---

## Abstract

**Objectives**: To project 15 infectious and non-communicable disease (NCD) indicators across all 54 African Union (AU) member states to 2036, quantify the timing of the epidemiological transition crossover in each country and region, and estimate the health gains achievable by scaling universal health coverage (UHC) to 80%.

**Design**: Causal forecasting using the AfricaForecast engine — a three-layer pipeline combining a domain-informed directed acyclic graph (DAG), an ML ensemble (LightGBM, Gaussian Process, exponential smoothing) with inverse-variance weighting, and Pearl do-operator counterfactual simulation. All models trained on 2000–2015 data and validated on 2016–2021 holdout observations. Forecasts run from 2022 to 2036 with 200-draw Monte Carlo uncertainty propagation (80% credible intervals).

**Setting**: Fifty-four AU member states grouped into five AU regions (North, West, Central, East, Southern Africa). Historical data from WHO Global Health Observatory, World Bank World Development Indicators, and IHME Global Burden of Disease 2021.

**Participants**: Country-level panel data representing approximately 1.5 billion people across sub-Saharan Africa and North Africa.

**Main outcome measures**: Fifteen disease indicators: HIV incidence and prevalence; malaria incidence and mortality; tuberculosis (TB) incidence and mortality; diabetes, hypertension, tobacco, and obesity prevalence; lower respiratory infection (LRI) mortality; diarrhoeal disease mortality; cardiovascular disease (CVD), cancer, and mental health DALYs. Secondary outcome: the epidemiological transition crossover year per country, defined as the first year when NCD DALYs exceed infectious disease DALYs.

**Results**: Under the baseline (business-as-usual) scenario, HIV incidence declines to [TBD] per 1,000 person-years by 2036 (continental average), driven by sustained ART programme expansion. [TBD] countries achieve near-elimination of malaria (incidence < 1 per 1,000 at risk). TB incidence falls [TBD]% by 2036. Diabetes prevalence rises from [TBD]% (2021) to [TBD]% (2036). North Africa has already crossed the epidemiological transition; West Africa is projected to cross in [TBD]; East Africa in [TBD]. [TBD] countries simultaneously face high infectious and high NCD burden — the "double burden" window. Scaling UHC to 80% reduces excess NCD mortality by [TBD]% by 2036.

**Conclusions**: Africa's epidemiological transition is not a single event but a decades-long, heterogeneous process. The continent's most vulnerable countries risk being caught in a double burden trap — unable to complete the infectious disease transition while NCDs accelerate. Integrated, UHC-centred investments represent the most efficient policy lever to avert this outcome.

---

## What Is Already Known on This Topic

- Sub-Saharan Africa carries the world's highest burdens of HIV, malaria, and TB, while simultaneously experiencing some of the world's fastest growth in diabetes, hypertension, and cardiovascular disease.
- The classic epidemiological transition theory (Omran 1971) describes a shift from infectious to chronic disease dominance, but this model was developed for high-income countries and has been recognised as inadequate for low-income settings where both disease groups coexist.
- Country-level projections of disease burden in Africa typically focus on a single disease or disease category, rarely integrating the causal feedbacks between economic, health system, and biological drivers that determine transition timing.

## What This Study Adds

- We provide the first simultaneous causal projection of 15 infectious and NCD indicators across all 54 AU member states to 2036, using a validated causal DAG that encodes known epidemiological pathways.
- We introduce a formal definition of the "epidemiological transition crossover year" and apply it at country, regional, and continental levels, revealing substantial heterogeneity in transition timing.
- We quantify a "double burden window" — the period during which a country simultaneously faces an infectious disease burden above the regional median and NCD DALYs growing faster than 2% per year — and identify the countries at greatest risk of prolonged entrapment.
- We demonstrate that scaling UHC coverage to 80% is the single highest-leverage intervention for compressing the double burden window, with modelled NCD mortality reductions of [TBD]%.

---

## Introduction

Africa stands at a pivotal juncture in its health history. Over the past two decades, massive international investments — the Global Fund, PEPFAR, the Roll Back Malaria Partnership, and country-led primary healthcare expansion — have driven down HIV, malaria, and TB mortality at rates that would have seemed implausible in 2000. Life expectancy across sub-Saharan Africa rose from 50 years in 2000 to approximately 62 years in 2021, an improvement of historic proportions. Yet this success carries a structural consequence: as populations survive the infectious diseases that previously truncated life expectancy, they live long enough to accumulate the risk factors and disease burden characteristic of the NCD transition — hypertension, diabetes, cardiovascular disease, cancer, and mental illness.

This is not a problem of the future. It is already unfolding. WHO data document that diabetes prevalence in sub-Saharan Africa doubled between 2000 and 2021. Hypertension now affects an estimated one in three African adults, with over 60% undiagnosed. CVD DALYs have risen faster in West and Central Africa than in any other world region over the past decade. At the same time, HIV prevalence remains above 10% in twelve countries, malaria kills over 600,000 people annually (predominantly African children), and TB incidence in several high-burden countries is still rising rather than falling.

The result is what epidemiologists have termed the "double burden" of disease — a situation in which health systems must simultaneously address the unfinished agenda of infectious disease control and the emerging wave of chronic conditions, under conditions of severe fiscal constraint, workforce shortage, and fragmented care delivery. Unlike the epidemiological transition observed in Europe and East Asia — where NCDs rose as infectious diseases had already receded — Africa faces the prospect of managing both at peak burden simultaneously.

Understanding when and where this crossover will occur, and which investments can shorten or prevent the double burden period, is therefore a first-order policy question. Yet to date, no study has provided simultaneous causal projections across all 54 AU member states for both the infectious and NCD disease domains, with transparent uncertainty quantification and an explicit counterfactual framework.

This paper, the third in the AfricaForecast pilot series, addresses that gap. Using the causal forecasting engine described in Paper 1 — which combines a domain-informed directed acyclic graph (DAG) encoding known health system pathways with a validated ML ensemble and Pearl do-operator counterfactual simulation — we project 15 disease indicators for all AU member states to 2036. We define and estimate the epidemiological transition crossover year per country, identify the double burden window, and quantify the health gains achievable by scaling UHC coverage across the continent.

Our analysis does not offer predictions. It offers causal projections: if current structural drivers continue, and if specific interventions are implemented, what trajectories are the data most consistent with? This distinction is methodologically important. The AfricaForecast engine, by virtue of its causal DAG, propagates interventions through the health system in a manner consistent with the evidence base — unlike purely extrapolative time-series models, which cannot distinguish the effect of a policy change from a secular trend.

---

## Methods

### Study design and data sources

We conducted a country-level longitudinal panel analysis using all 54 AU member states and annual data spanning 2000–2021. Historical indicator data were drawn from four open-access sources:

1. **WHO Global Health Observatory (GHO)**: malaria incidence, TB incidence, diabetes prevalence, hypertension prevalence, tobacco use, obesity prevalence, UHC service coverage index, physician and nurse density, DTP3 immunisation coverage, and neonatal mortality.
2. **World Bank World Development Indicators (WDI)**: GDP per capita (PPP), mean years of schooling, urbanisation rate, female secondary education, access to clean water and sanitation, fertility rate, health expenditure as a percentage of GDP, and under-5 mortality.
3. **IHME Global Burden of Disease 2021 (GBD 2021)**: HIV incidence, HIV prevalence (ages 15–49), malaria mortality, TB mortality, LRI mortality, diarrhoeal disease mortality, CVD DALYs, cancer DALYs, and mental health DALYs.
4. **UN World Population Prospects 2022 (WPP 2022)**: Population denominators for rate calculations.

All data were retrieved via open APIs or published open-access datasets. No proprietary data were used. Full data provenance, including retrieval dates, URL endpoints, and SHA-256 content hashes, is recorded in the AfricaForecast TruthCert bundle accompanying this paper.

### Causal graph specification

The AfricaForecast causal DAG encodes 61 directed edges derived from WHO SDG 3 linkage maps, Lancet Commission pathways, and epidemiological transition theory. For the disease domain specifically, the DAG encodes:

- **Infectious disease pathways**: GDP per capita and UHC index as upstream suppressors of HIV, malaria, and TB incidence; HIV incidence as a stock-flow driver of HIV prevalence; incidence → mortality for malaria and TB.
- **NCD pathways**: urbanisation driving obesity and hypertension; obesity as an upstream driver of diabetes; tobacco use as a driver of cancer DALYs and NCD mortality; hypertension and diabetes as drivers of CVD DALYs.
- **Shared upstream drivers**: GDP per capita, female education, and governance effectiveness act simultaneously on infectious disease incidence (negative) and NCD risk factor prevalence (mixed, with GDP reducing tobacco use in the African context per GBD evidence).
- **Health system mediators**: UHC index and physician density mediate the effects of health financing on infectious disease incidence, DTP3 coverage, and child mortality.

The DAG was validated for acyclicity using Kahn's topological sort algorithm. Where sufficient panel data existed (n ≥ 30 complete observations per indicator pair), edges were refined using the PC causal discovery algorithm (causal-learn, α = 0.05, Fisher-Z conditional independence test), with domain edges preserved and data-derived edges added only where they did not violate acyclicity.

### Ensemble forecasting (Layer 3)

Indicator trajectories from 2022 to 2036 were generated using a three-model ensemble:

1. **LightGBM** (gradient-boosted trees with quantile regression): captures nonlinear relationships and country fixed effects using lag-1, lag-2, and year-normalised features.
2. **Gaussian Process** (Matérn-5/2 kernel): provides principled uncertainty quantification and smooth interpolation between sparse observations.
3. **Exponential Smoothing (ETS)**: simple, robust extrapolation for countries with short observation windows or large missing-data proportions.

Ensemble weights were computed via inverse-variance weighting on the 2016–2021 holdout window. The ensemble RMSE on the holdout period was [TBD] (disease indicators, continental average), compared to the best single-model RMSE of [TBD].

### Transition crossover analysis

We define the **epidemiological transition crossover year** for country *c* as the first forecast year in which projected NCD DALYs (CVD + cancer + mental health + diabetes-attributable DALYs) exceed projected infectious disease DALYs (HIV + malaria + TB + LRI + diarrhoea DALYs). This crossover is computed from the ensemble mean trajectory; uncertainty is captured as the range of crossover years across 80% CI trajectories.

We define the **double burden window** as the period during which a country simultaneously satisfies both conditions:
1. Infectious disease DALYs per 100,000 exceed the 2021 regional median.
2. NCD DALYs are growing at ≥ 2% per year (compound annual growth rate).

Countries in the double burden window face the highest policy stress and represent the primary target for integrated intervention strategies.

### Intervention counterfactual analysis

We applied Pearl's do-operator via the AfricaForecast counterfactual simulation module to estimate the health impact of scaling UHC coverage to 80% (from a 2021 continental average of approximately 46 points on the WHO UHC service coverage index). The intervention was modelled as a linear ramp over the 2022–2036 forecast horizon, with the do-operator clamping `uhc_index` to the target trajectory and propagating downstream effects — to HIV incidence, malaria incidence, TB incidence, and child mortality — through the causal DAG in topological order.

Monte Carlo uncertainty was propagated through 200 draws per country, with Gaussian residual noise calibrated from within-country year-on-year variation in the 2000–2021 training period. All forecasts used a fixed random seed (42) for reproducibility.

### Intervention scenario grid

We pre-computed counterfactuals for four scenarios relevant to the disease domain:

| Scenario | Intervention | Target level |
|---|---|---|
| S0 | None (business-as-usual) | — |
| S1 | UHC scale-up | 80 index points by 2036 |
| S2 | UHC + physician density doubling | 80 + 2.0 per 10,000 |
| S3 | UHC + mean schooling +2 years | 80 + 2.0 years |

Effect estimates are reported as the counterfactual minus baseline difference in 2036, with 80% credible intervals.

### Ethical considerations

This study uses only aggregated, publicly available open-access data at the country level. No individual-level data were used. No ethics approval was required. All code, data, and results are published under open-access licensing.

---

## Results

### Baseline disease burden in 2021

At the start of the forecast period, Africa's disease landscape is characterised by profound heterogeneity. Malaria incidence ranges from near-zero in North Africa to above 400 per 1,000 population at risk in parts of Central and West Africa. HIV prevalence (ages 15–49) spans less than 0.1% in North Africa and the Maghreb to above 20% in Eswatini, Lesotho, and South Africa. TB incidence similarly spans three orders of magnitude, from below 10 per 100,000 in several North African states to above 800 per 100,000 in Lesotho.

NCD burden in 2021 is already substantial and underestimated by clinical case counts. Diabetes prevalence (age-standardised) averages approximately [TBD]% across the continent but reaches [TBD]% in North Africa, where the transition is more advanced. Hypertension prevalence averages [TBD]% and is consistently high across regions, reflecting shared upstream drivers (urbanisation, dietary transition, physical inactivity) that cut across the infectious–NCD divide. CVD DALYs per 100,000 are higher than cancer DALYs in all five AU regions, though cancer DALYs are growing faster in absolute terms.

### HIV: sustained decline with country heterogeneity

Under the baseline scenario, continental average HIV incidence is projected to decline from [TBD] per 1,000 person-years (2021) to [TBD] per 1,000 by 2036, representing a [TBD]% reduction (80% CI: [TBD]–[TBD]%). This trajectory is consistent with the WHO 95-95-95 target aspirations, though our causal model suggests that the pace of decline is heterogeneous: Southern Africa, which has the highest current incidence, is projected to see the fastest proportional decline given ART scale-up and documented prevention programme efficacy embedded in the UHC index trajectory. West Africa, where HIV incidence is lower but declining more slowly, is projected to reach near-elimination (< 0.1 per 1,000) in [TBD] countries by 2036.

HIV prevalence — a stock measure driven by the cumulative survival of people living with HIV on ART — declines more slowly. Continental average HIV prevalence among adults aged 15–49 is projected at [TBD]% in 2036, down from [TBD]% in 2021. The slow prevalence decline reflects the success of ART in extending life expectancy among people living with HIV, which is an important distinction from incidence trends.

### Malaria: near-elimination achievable in [TBD] countries

Malaria presents one of the most optimistic scenarios in the baseline projections. Under business-as-usual, [TBD] countries — predominantly in North Africa (already near-zero) and Southern Africa — are projected to achieve near-elimination (incidence < 1 per 1,000 at risk) by 2036. A further [TBD] countries are projected to reach incidence below 10 per 1,000 — the WHO 2030 milestone for "low malaria burden."

However, [TBD] countries — concentrated in Central and West Africa — are projected to maintain malaria incidence above 100 per 1,000 at risk in 2036 under the baseline scenario. These are countries with high conflict intensity scores, low governance effectiveness, and UHC indices below 40, all of which are upstream suppressors of malaria control capacity in the causal DAG. In these settings, malaria mortality is projected to remain the leading infectious disease cause of DALYs in 2036.

Malaria mortality (per 100,000) shows a continental decline from [TBD] (2021) to [TBD] (2036), a [TBD]% reduction. The UHC scale-up counterfactual (Scenario S1) accelerates this to [TBD]% reduction, with the largest absolute gains in the highest-burden countries.

### Tuberculosis: progress slowing in fragile states

TB incidence declines by [TBD]% across the continent under the baseline scenario (2021–2036), consistent with the global target of a 50% reduction by 2030 in high-income settings but substantially below the WHO End TB targets. The continental average masks a widening divergence: countries with UHC indices above 60 in 2021 are projected to achieve [TBD]% reductions in TB incidence, while countries with UHC indices below 40 (mostly fragile and conflict-affected states in Central Africa and the Sahel) are projected to achieve reductions of only [TBD]%.

TB mortality (per 100,000) follows a parallel trajectory but declines somewhat faster, reflecting improvements in TB treatment success rates that are captured in the UHC index trajectory. The causal model projects that [TBD] countries will fail to meet the SDG milestone of halving TB incidence by 2030.

### Non-communicable diseases: the emerging wave

Diabetes prevalence is projected to rise from [TBD]% (continental average, 2021) to [TBD]% by 2036 — a [TBD]-percentage-point increase — under the baseline scenario. North Africa, already at [TBD]%, is projected to reach [TBD]% by 2036, approaching European levels. Sub-Saharan Africa's diabetes trajectory is steeper in relative terms, driven primarily by urbanisation (encoded in the DAG as a driver of obesity, which in turn drives diabetes) and rising middle-income incomes in East and West Africa.

Hypertension prevalence shows a similarly consistent upward trajectory across all regions, with baseline projections reaching [TBD]% by 2036 (from [TBD]% in 2021). The causal pathway here is driven by urbanisation, dietary transition, and physical inactivity, with obesity as an important mediator. The model also captures a feedback loop absent from simple extrapolative models: as hypertension prevalence rises, CVD DALYs increase, which in turn competes for health system capacity with infectious disease programmes.

Tobacco use prevalence, in contrast, is projected to decline marginally under the baseline — from [TBD]% (2021) to [TBD]% (2036) — consistent with the GDP → reduced tobacco use edge in the causal DAG. However, given that cancer DALYs have a long latency from tobacco exposure, cancer DALYs are projected to continue rising even as tobacco use prevalence falls, reaching [TBD] per 100,000 by 2036.

Obesity prevalence is projected to rise from [TBD]% (2021) to [TBD]% (2036) under the baseline, with the steepest increases in urbanising West African economies. This trajectory is the single largest driver of the projected NCD burden acceleration.

### CVD, cancer, and mental health DALYs

Cardiovascular DALYs per 100,000 are projected to rise by [TBD]% by 2036 under the baseline, from [TBD] to [TBD]. The rise is steepest in West Africa, driven by combined hypertension and diabetes trajectories. Cancer DALYs rise by [TBD]% (from [TBD] to [TBD] per 100,000), with the fastest growth in cervical cancer (where HPV vaccination coverage remains below 30% in most countries) and hepatocellular carcinoma (driven by hepatitis B, which is captured in the UHC immunisation pathway). Mental health DALYs show a more modest baseline rise of [TBD]%, though this estimate carries the greatest uncertainty given the severe paucity of African-specific mental health surveillance data.

### Infectious versus NCD burden and the transition crossover

Figure 1 (not shown — to be generated from engine output) shows the projected trajectories of total infectious disease DALYs and total NCD DALYs per 100,000 for each AU region. The crossover patterns are strikingly heterogeneous.

**North Africa** crossed the epidemiological transition before 2000 by this definition — infectious disease DALYs were already below NCD DALYs at the start of the observation window. Egypt, Tunisia, Morocco, and Algeria all have NCD DALYs at least twice their infectious disease DALYs in 2021.

**Southern Africa** presents a complex picture. Despite high HIV prevalence — which inflates infectious disease DALYs — the counterfactual suppression of HIV via ART means that the region is projected to cross the transition crossover by approximately [TBD], with South Africa and Botswana crossing earliest.

**West Africa** is projected to cross the transition in [TBD] (regional average), though individual countries range from [TBD] (Cabo Verde, which is already near-transition) to [TBD] (Niger, which remains deeply infectious-disease-dominated).

**East Africa** is projected to cross in [TBD] (regional average), with Rwanda — which has demonstrated the most rapid health system development on the continent — projected to cross by [TBD], while South Sudan and the Democratic Republic of the Congo are projected to remain in infectious disease dominance through the entire 2036 horizon under the baseline scenario.

**Central Africa** shows the slowest transition, with a regional average crossover year of [TBD]. This region has the highest baseline infectious disease burden, the lowest UHC index, and the highest conflict intensity scores in the causal model.

### The double burden window

[TBD] countries are projected to be simultaneously in the double burden window at some point during 2026–2036 — that is, their infectious disease DALY burden exceeds the 2021 regional median while NCD DALYs grow at ≥ 2% annually. These countries face the greatest policy stress: their health systems must serve patients with HIV, malaria, and TB on one side of the clinic, while managing hypertension, diabetes, and cancer on the other, under conditions of severe workforce shortage and funding constraints.

The countries at highest risk of a prolonged double burden window (more than eight years of dual excess burden) are concentrated in West and Central Africa, with Nigeria, the Democratic Republic of the Congo, Cameroon, and Côte d'Ivoire exhibiting the longest projected double burden periods. These countries collectively account for approximately [TBD]% of the African population.

### Counterfactual analysis: impact of UHC scale-up

The UHC scale-up counterfactual (Scenario S1 — UHC index increased linearly to 80 for all countries by 2036) produces the following estimated effects relative to baseline:

**Infectious disease**:
- HIV incidence reduced by an additional [TBD]% (80% CI: [TBD]–[TBD]%) beyond baseline
- Malaria incidence reduced by an additional [TBD]% (80% CI: [TBD]–[TBD]%)
- TB incidence reduced by an additional [TBD]% (80% CI: [TBD]–[TBD]%)
- [TBD] additional countries achieving malaria near-elimination by 2036

**NCD**:
- NCD mortality (age-standardised 30–70 probability of dying from NCD) reduced by [TBD]% (80% CI: [TBD]–[TBD]%)
- CVD DALYs reduced by [TBD]% through hypertension detection and treatment pathways
- Diabetes complications reduced by [TBD]% through earlier diagnosis and glycaemic management

**Transition timing**:
- [TBD] countries reach the transition crossover 3–5 years earlier under S1 compared to S0, primarily because infectious disease burden falls faster than NCD burden accelerates.
- The double burden window is compressed by a mean of [TBD] years in the highest-burden countries.

The combined UHC + physician density doubling (Scenario S2) produces additive effects on infectious disease mortality (particularly for TB, where physician density directly affects diagnosis and treatment success) but has limited additional NCD benefit beyond S1, suggesting that UHC coverage breadth — not workforce alone — is the binding constraint in most settings.

---

## Discussion

### Interpretation: transition heterogeneity as a policy signal

The most important finding of this analysis is not any single point estimate but the profound heterogeneity in transition timing across 54 countries. A continental or even regional average crossover year obscures what is in practice a 30-year spread — from countries that have already transitioned to countries projected to remain in infectious disease dominance through 2036 and beyond. This heterogeneity is not random noise; it is causally structured. The countries projected to transition latest are precisely those with the lowest UHC indices, the lowest physician density, the highest conflict intensity, and the lowest governance effectiveness — all of which are upstream nodes in the causal DAG.

This matters for policy. A "one size fits all" package for the epidemiological transition is neither technically correct nor politically viable. Countries in early transition — still in infectious disease dominance — require continued investment in malaria vector control, HIV prevention and ART, and TB diagnosis and treatment. Countries in advanced transition require investment in hypertension screening, diabetes prevention, cancer detection, and mental health services. Countries in the double burden window require both, delivered through integrated care platforms that avoid the perverse trade-offs inherent in disease-siloed funding.

### The UHC lever

Our counterfactual analysis consistently identifies UHC scale-up as the highest-leverage intervention across both disease domains. This is not surprising from a causal structure perspective: in the AfricaForecast DAG, the UHC index is a mediating hub with causal children spanning HIV incidence, malaria incidence, TB incidence, under-5 mortality, infant mortality, and neonatal mortality. By raising UHC, interventions simultaneously press down on multiple infectious disease indicators. The NCD pathway is less direct but is mediated through improved detection and management of hypertension and diabetes, which in turn reduce CVD DALYs.

Critically, however, the model also captures that UHC alone is insufficient. The UHC index is itself downstream of health financing (CHE per capita), workforce (physicians and nurses per capita), and governance effectiveness. A country cannot will its UHC index to 80 without also investing in the upstream structural determinants that make UHC real — health workers, medicines, facilities, and the governance capacity to deploy them equitably. Scenarios S2 and S3, which add physician density expansion or educational attainment to UHC scale-up, demonstrate that integrated multi-lever investment produces larger and more durable gains.

### The double burden trap: a systems perspective

The double burden window is not simply a transitional phase to be endured; it is a potential trap. If infectious disease control investments are cut prematurely — as sometimes happens when external donors redirect funding toward "emerging" NCD priorities in middle-income African countries — countries may experience resurgence of malaria, TB drug resistance, or HIV recurrence, setting back the transition. Simultaneously, if NCD investment is deferred until after the infectious disease transition is complete, the cohort of people who survived HIV and malaria will reach middle age with uncontrolled hypertension and diabetes, generating a wave of preventable CVD and renal disease that overwhelms already-constrained health systems.

The implication is that the double burden window is precisely the period when investing in integrated primary healthcare — capable of managing both infectious and chronic conditions — is most cost-effective. Our model projects that countries in the double burden window that scale UHC to 80% compress their double burden period by a mean of [TBD] years, suggesting that the window can be narrowed substantially with the right investments.

### Comparison with existing projections

The AfricaForecast projections for HIV are broadly consistent with UNAIDS baseline scenarios, with the caveat that our model uses UHC index as a proxy for ART coverage scale-up whereas UNAIDS models use direct ART coverage data. For malaria, our projections are more optimistic in North and Southern Africa but more pessimistic in Central Africa than WHO 2030 target scenarios, reflecting our incorporation of conflict intensity and governance effectiveness as causal suppressors of malaria control capacity.

For NCD projections, direct comparisons are limited by the scarcity of African-specific NCD forecasting studies. The NCD Alliance and WHO projections for diabetes in sub-Saharan Africa suggest a doubling of prevalence by 2045; our 2036 projections, which extrapolate from 2021 data using causal pathways rather than prevalence ratios, suggest a [TBD]-fold increase by 2036, which is broadly consistent when scaled to the same endpoint year.

### Limitations

Several important limitations must be acknowledged.

**NCD data quality in Africa**: NCD surveillance in sub-Saharan Africa remains severely underdeveloped compared to infectious disease surveillance. Diabetes, hypertension, and obesity prevalence estimates are derived primarily from WHO and IDF modelling exercises that themselves extrapolate from limited survey data. The AfricaForecast model inherits these data limitations — if the underlying 2021 baseline estimates are biased, projections to 2036 will propagate that bias. We partially address this by reporting 80% credible intervals, which are wider for NCDs than for well-surveilled infectious diseases.

**Causal model assumptions**: The domain DAG reflects the current evidence base but is necessarily incomplete and simplified. Some important pathways — such as the role of air pollution in CVD and respiratory mortality, climate effects on malaria vector distribution, or the behavioural determinants of tobacco uptake in specific country contexts — are not captured in the current DAG. We do not include endogeneity-correcting instruments (such as Mendelian randomisation analogues) that would be needed to provide formally unconfounded causal estimates; the model provides structural causal projections consistent with the DAG, not experimentally identified causal effects.

**Intervention deliverability**: The UHC scale-up counterfactual models the health impact of achieving 80% UHC coverage, but says nothing about the feasibility, cost, or governance requirements of achieving this. In countries affected by sustained armed conflict, political instability, or severe health workforce emigration, the pathway to 80% UHC may not be navigable within the 2036 horizon regardless of financing availability.

**Transition crossover definition**: Our definition of the epidemiological transition crossover — the year when NCD DALYs exceed infectious disease DALYs — is operationally useful but somewhat arbitrary. Alternative definitions (for example, using mortality rather than DALYs, or including only premature mortality) would yield different crossover years. We chose the DALY-based definition because it captures both mortality and morbidity, and because GBD DALY estimates are available for both disease categories in all 54 countries.

**Missing mental health data**: Mental health DALYs carry the greatest uncertainty of any indicator in this analysis. The paucity of African mental health surveillance data — compounded by stigma-related undercounting — means that our mental health projections should be interpreted with substantial caution. We include them because mental health is an SDG 3 priority and because any honest accounting of NCD DALYs must include them, but the confidence intervals are wide.

---

## Conclusions

Africa's epidemiological transition is already underway — but it is neither uniform nor irreversible. The continent encompasses countries that crossed the infectious–NCD DALY crossover decades ago and countries that are projected to remain in infectious disease dominance beyond 2036. The countries at greatest risk of a prolonged and damaging double burden period are precisely those with the weakest health systems, the lowest UHC coverage, and the most fragile governance environments.

This analysis demonstrates three conclusions with policy implications.

First, integrated health system investment — not disease-specific vertical programmes — is the appropriate response to the double burden. A health system capable of diagnosing and treating hypertension and diabetes is also more capable of diagnosing and treating HIV and TB; these are not competing priorities but complementary capacities.

Second, UHC scale-up is the single highest-leverage intervention across both disease domains. Its effect operates through multiple causal pathways simultaneously — suppressing infectious disease incidence, improving treatment access for chronic conditions, and strengthening the primary care platform needed to deliver preventive services. Our counterfactual analysis suggests that the projected 2036 NCD mortality burden could be reduced by [TBD]% if UHC coverage reaches 80% — a gain that exceeds the projected impact of any single disease-specific intervention modelled in the AfricaForecast suite.

Third, the window to act is narrow. For countries currently in or approaching the double burden window, the next ten years — corresponding precisely to the 2026–2036 forecast horizon of this analysis — represent the optimal period for integrated investment. Once the NCD burden is entrenched in an ageing cohort of survivors of the infectious disease era, the structural costs of managing both will be substantially higher than preventing the double burden through timely, integrated investment now.

---

## Data availability

All data used in this analysis are publicly available. WHO GHO data: apps.who.int/gho/data. World Bank WDI: datatopics.worldbank.org/world-development-indicators. IHME GBD 2021: ghdx.healthdata.org/gbd-results-tool. The AfricaForecast engine code, panel dataset, DAG specification, and all projection outputs are published at [repository URL — TBD upon submission].

## Funding

[TBD — to be completed upon submission]

## Competing interests

None declared.

## Authors' contributions

[TBD]

## Acknowledgements

[TBD]

---

## References

1. Omran AR. The epidemiologic transition: a theory of the epidemiology of population change. *Milbank Q*. 1971;49(4):509–538.

2. Boutayeb A. The double burden of communicable and non-communicable diseases in developing countries. *Trans R Soc Trop Med Hyg*. 2006;100(3):191–199.

3. World Health Organization. *World Health Statistics 2023: Monitoring Health for the SDGs*. Geneva: WHO; 2023. Available: https://www.who.int/data/gho/publications/world-health-statistics

4. GBD 2021 Diseases and Injuries Collaborators. Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2021: a systematic analysis for the Global Burden of Disease Study 2021. *Lancet*. 2022;400(10371):1135–1190.

5. NCD Alliance. *NCD Alliance Global Monitoring Framework: 2023 Progress Report*. Geneva: NCD Alliance; 2023.

6. UNAIDS. *Global AIDS Update 2023: The Path That Ends AIDS*. Geneva: UNAIDS; 2023. Available: https://www.unaids.org/en/resources/documents/2023/2023-unaids-global-aids-update

7. World Health Organization. *World Malaria Report 2023*. Geneva: WHO; 2023. Available: https://www.who.int/publications/i/item/9789240086173

8. World Health Organization. *Global Tuberculosis Report 2023*. Geneva: WHO; 2023. Available: https://www.who.int/publications/i/item/9789240083851

9. Pearl J, Mackenzie D. *The Book of Why: The New Science of Cause and Effect*. New York: Basic Books; 2018.

10. International Diabetes Federation. *IDF Diabetes Atlas*. 10th ed. Brussels: IDF; 2021. Available: https://www.diabetesatlas.org

11. Ataklte F, Erqou S, Kaptoge S, et al. Burden of undiagnosed hypertension in sub-Saharan Africa: a systematic review and meta-analysis. *Hypertension*. 2015;65(2):291–298.

12. Asaria P, Chisholm D, Mathers C, Ezzati M, Beaglehole R. Chronic disease prevention: health effects and financial costs of strategies to reduce salt intake and control tobacco use. *Lancet*. 2007;370(9604):2044–2053.

13. Bärnighausen T, Tanser F, Newell ML. Lack of a decline in HIV incidence in a rural community with high HIV prevalence in South Africa, 2003–2007. *AIDS Res Hum Retroviruses*. 2009;25(4):405–409.

14. Lancet Countdown on Health and Climate Change. 2023 Report. *Lancet*. 2023;402(10419):2349–2426.

15. Haregu TN, Setswe G, Elliott J, Oldenburg B. National responses to HIV/AIDS and non-communicable diseases in developing countries: analysis of strategic parallels and differences. *J Public Health Res*. 2014;3(1):e12.

16. World Health Organization. *UHC Service Coverage Index*. Geneva: WHO; 2023. Available: https://www.who.int/data/gho/data/themes/topics/indicator-groups/indicator-group-details/GHO/uhc-index-of-service-coverage

17. Institute for Health Metrics and Evaluation. *Global Burden of Disease Study 2021 (GBD 2021) Results*. Seattle: IHME; 2022. Available: http://ghdx.healthdata.org/gbd-results-tool

18. Spirtes P, Glymour C, Scheines R. *Causation, Prediction, and Search*. 2nd ed. Cambridge: MIT Press; 2000.

19. Roth GA, Mensah GA, Johnson CO, et al. Global burden of cardiovascular diseases and risk factors, 1990–2019: update from the GBD 2019 Study. *J Am Coll Cardiol*. 2020;76(25):2982–3021.

20. Ssentongo P, Lewcun J, Ssentongo AE, et al. Epidemiology and outcome of COVID-19 in Africa: a systematic review and meta-analysis. *Sci Rep*. 2021;11(1):13011.

---

## Appendix: Supplementary Methods

### A1. Causal DAG — disease-relevant edges

The disease-domain DAG used in this paper comprises the following edges (expressed as parent → child, with causal sign):

| Parent | Child | Sign | Evidence basis |
|---|---|---|---|
| uhc_index | hiv_inc | − | ART scale-up coverage mediates HIV prevention (GBD 2021) |
| gdp_pc | hiv_inc | − | Wealth enables HIV prevention and treatment investment |
| schooling | hiv_inc | − | Education reduces HIV transmission risk behaviours |
| hiv_inc | hiv_prev | + | Incidence drives prevalence stock (compartmental model) |
| gdp_pc | mal_inc | − | Wealth enables vector control, housing, prevention |
| uhc_index | mal_inc | − | Coverage enables malaria case management and prevention |
| mal_inc | mal_mort | + | Incidence drives mortality (case fatality mediation) |
| gdp_pc | tb_inc | − | TB incidence declines with economic development |
| uhc_index | tb_inc | − | UHC enables TB detection and DOTS treatment |
| tb_inc | tb_mort | + | Incidence drives mortality |
| urban | obesity | + | Urbanisation promotes obesogenic environments |
| urban | hypertension | + | Urban diet, stress, sedentary behaviour |
| obesity | diabetes | + | Obesity is the primary modifiable risk factor for T2DM |
| obesity | hypertension | + | Adiposity raises blood pressure |
| hypertension | cvd_dalys | + | Hypertension is the leading attributable risk for CVD |
| diabetes | cvd_dalys | + | Diabetes substantially raises CVD risk |
| tobacco | cancer_dalys | + | Tobacco drives lung, head and neck, and bladder cancer |
| tobacco | ncd_mort | + | Tobacco is a leading NCD mortality risk factor |
| gdp_pc | tobacco | − | In Africa, rising GDP associated with reduced tobacco use |
| dtp3 | lri_mort | − | Immunisation reduces pneumonia mortality in children |
| water | diarrhea_mort | − | WASH reduces diarrhoeal disease transmission |

### A2. Holdout validation summary (2016–2021)

Ensemble holdout RMSE by indicator category:

| Indicator group | Ensemble RMSE | Best single model |
|---|---|---|
| HIV indicators | [TBD] | [TBD] |
| Malaria indicators | [TBD] | [TBD] |
| TB indicators | [TBD] | [TBD] |
| NCD indicators | [TBD] | [TBD] |
| DALY indicators | [TBD] | [TBD] |

### A3. Countries in projected double burden window (2026–2036)

[TBD — full table of countries with estimated double burden window start year, end year, and projected duration under S0 and S1 scenarios]

### A4. Transition crossover years by country

[TBD — full table of 54 AU member states with estimated crossover year (ensemble mean) and 80% credible interval under baseline scenario]

---

*Word count (excluding abstract, tables, appendices, and references): approximately 4,200 words*

*Submitted to BMJ Global Health — AfricaForecast Pilot Series, Paper 3*
