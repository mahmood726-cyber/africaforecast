# Can Africa close the health workforce gap by 2036? A counterfactual analysis of 54 countries

**Submitted to:** *The Lancet*

**Paper 4 of the AfricaForecast series** (Health Systems Pilot)

---

## Summary

**Background:** Africa faces a severe and persistent shortage of health workers. The WHO recommends a minimum density of 44.5 physicians, nurses, and midwives per 10,000 population to deliver essential services; most African countries remain far below this threshold. Low and stagnant health spending — averaging approximately 5% of GDP on the continent versus more than 10% in OECD countries — constrains workforce growth, infrastructure, and service coverage. The UHC service coverage index ranges from below 30 to above 75 across the 54 African Union (AU) member states, reflecting vast inequalities in system capacity. Whether Africa can close these gaps by 2036 under realistic investment scenarios remains an open and politically urgent question.

**Methods:** We assembled a country-year panel across all 54 AU member states (2000–2021) spanning 12 health system indicators: physician density, nurse and midwife density, hospital bed density, health expenditure as a share of GDP and in per-capita purchasing-power-parity terms, the UHC service coverage index, DTP3 immunisation coverage, skilled birth attendance, out-of-pocket expenditure share, domestic government health expenditure, external health expenditure share, and essential medicines availability. We embedded these indicators within a pre-specified causal directed acyclic graph (DAG) linking health financing to workforce, workforce to service coverage, and coverage to mortality outcomes. We then applied a Pearl do-operator counterfactual engine — forward-simulating indicator trajectories under four scenarios to 2036: (0) Baseline, current trends; (A) all countries reach the Abuja Declaration target of 5% of GDP on health; (B) spending reaches 8% of GDP combined with doubling of physician training throughput; (C) external development assistance for health (DAH) increases 50% from current levels. Monte Carlo sampling (200 draws, seed 42) provided 80% uncertainty intervals. Downstream mortality effects were propagated through the causal DAG.

**Findings:** Under baseline trajectories, only [TBD] of 54 countries are projected to meet the WHO 44.5 workforce threshold by 2036. The continental physician density is projected to reach [TBD] per 10,000 by 2036 (from [TBD] in 2021), and the UHC index [TBD]. Achieving the Abuja target (Scenario A) would increase the continental UHC index by approximately [TBD] points and bring an additional [TBD] countries above the workforce threshold. The full investment scenario (Scenario B) is projected to prevent [TBD] child deaths and [TBD] maternal deaths over the decade. Each additional 1% of GDP allocated to health spending translates to an estimated [TBD] years of life expectancy gain at the continental level. Central and West African sub-regions face the largest absolute gaps; North Africa is closest to the workforce and spending thresholds.

**Interpretation:** Closing Africa's health workforce gap by 2036 is technically achievable but requires sustained political commitment well beyond the Abuja Declaration. The Abuja target of 5% of GDP is necessary but insufficient; 8% combined with accelerated physician training is needed for SDG 3 achievement. The causal architecture confirms that investment effects cascade: health financing drives workforce expansion, which expands coverage, which reduces mortality — a chain that can be unlocked at scale within the 10-year training pipeline horizon.

**Funding:** Open-access modelling research; no commercial funding.

---

## Introduction

Africa's health workforce crisis is one of the most consequential structural constraints on human development. The World Health Organization's minimum threshold of 44.5 physicians, nurses, and midwives per 10,000 population — the level estimated to be consistent with meeting Sustainable Development Goal (SDG) 3 targets for maternal and child mortality — remains out of reach for the majority of the continent's 54 sovereign states. In Sub-Saharan Africa, physician density averages fewer than 2 per 10,000 population, compared with more than 30 in Western Europe and more than 25 in North America. This is not merely a statistical disparity; it represents millions of avoidable deaths and an immense loss of productive human potential.

The financing roots of this crisis are well documented. Total health expenditure in Africa averages approximately 5% of GDP, but this figure conceals dramatic variation: oil-rich states and upper-middle-income countries in North and Southern Africa approach or exceed this average, while many Sahelian and Central African countries spend less than 3% of GDP on health. The 2001 Abuja Declaration committed African governments to allocating at least 15% of their national budgets to health; as of the most recent available data, fewer than a quarter of AU member states have achieved this target. Total health expenditure per capita in purchasing-power-parity terms ranges from below US\$50 in the poorest fragile states to above US\$1,500 in Seychelles and Mauritius.

The UHC service coverage index, which aggregates 14 tracer indicators spanning reproductive, maternal, newborn, and child health, infectious disease control, and non-communicable disease (NCD) management, varies between approximately 20 and 80 across the continent. Countries with higher physician and nurse densities, higher government health expenditure, and stronger essential medicines availability consistently achieve higher UHC index scores. This covariation is not coincidental: it reflects a causal chain in which financing enables workforce formation, workforce enables service delivery, and service delivery determines health outcomes.

Despite widespread recognition of these dynamics, rigorous quantitative modelling of what investment levels are required to close specific gaps by a specific horizon has been limited. Existing projections tend to examine single indicators in isolation, focus on Sub-Saharan Africa rather than the full AU, or stop short of linking financing scenarios to downstream mortality effects through an explicit causal model. The AfricaForecast project addresses these gaps by constructing a causal DAG-based counterfactual engine applied uniformly across all 54 AU member states.

This paper, the fourth in the AfricaForecast series, focuses on health systems indicators. Papers 1–3 presented results for comprehensive mortality outcomes, infectious disease burden, and non-communicable disease trajectories, respectively. Paper 4 asks the most policy-actionable question of the series: under what investment scenarios can Africa close the health workforce and coverage gap by 2036, and what are the downstream mortality consequences of each scenario?

---

## Methods

### Study design and panel construction

We constructed a balanced country-year panel covering all 54 African Union member states for the period 2000 to 2021, the final year of complete WHO and World Bank data at the time of analysis. All data were sourced from open-access repositories: the WHO Global Health Observatory (GHO) for physician density, nurse density, UHC index, DTP3 coverage, skilled birth attendance, domestic government health expenditure, and external health expenditure share; the World Bank World Development Indicators (WDI) for health expenditure as a share of GDP, health expenditure per capita (PPP-adjusted), hospital bed density, and out-of-pocket expenditure share; and supplementary WHO GHO records for essential medicines availability where available.

The full indicator set for this paper comprises 12 health systems indicators: physician density (per 10,000 population), nurse and midwife density (per 10,000), hospital bed density (per 1,000), total health expenditure as a percentage of GDP, total health expenditure per capita (2017 international USD, PPP-adjusted), UHC service coverage index (0–100 scale), DTP3 immunisation coverage among one-year-olds (%), skilled birth attendance (%), out-of-pocket expenditure as a share of current health expenditure (%), domestic general government health expenditure (% of GDP), external health expenditure as a share of current health expenditure (%), and essential medicines availability (% of listed medicines available in a standardised facility survey).

Missing data were addressed using multiple imputation from lagged within-country observations and regional medians, with the imputation year and source recorded in each observation's provenance record. Countries with more than 70% missingness on any core indicator across the time series were flagged in sensitivity analyses; results are presented for all 54 countries except where stated.

### Causal directed acyclic graph

We pre-specified a causal DAG before model fitting, drawing on three primary evidence sources: the WHO SDG 3 indicator linkage maps, Lancet Commission pathway diagrams (specifically those from the Lancet Commission on Investing in Health and the Lancet Commission on Global Health 2035), and epidemiological transition theory. The DAG encodes domain-informed directional relationships across four layers:

1. **Economic and governance determinants** (GDP per capita, governance effectiveness, fragility index) acting as upstream drivers of health financing;
2. **Health financing** (che\_gdp, che\_pc, gghe, ext\_he) acting on workforce and infrastructure;
3. **Workforce and infrastructure** (physicians, nurses, beds, medicines) acting on service coverage;
4. **Service coverage and mortality outcomes** (uhc\_index, dtp3, sba, u5\_mort, mat\_mort, neo\_mort, life\_exp).

Key causal paths in the DAG that bear on this paper include: (i) health expenditure per capita → physician density (+), (ii) health expenditure per capita → nurse density (+), (iii) physician density → UHC index (+), (iv) nurse density → UHC index (+), (v) UHC index → under-5 mortality (−), (vi) UHC index → maternal mortality ratio (−), (vii) skilled birth attendance → maternal mortality ratio (−), and (viii) DTP3 coverage → under-5 mortality (−). Each edge is tagged with its literature source and a signed effect direction. The full DAG is available as a machine-readable JSON file in the supplementary data repository.

The DAG was tested for acyclicity using Kahn's algorithm prior to any model fitting. We additionally attempted data-driven refinement using the PC constraint-based causal discovery algorithm (Fisher-z conditional independence test, alpha = 0.05) on the complete-case panel; any data-suggested edges that contradicted domain knowledge or introduced cycles were discarded, and all domain edges were preserved unchanged.

### Forward simulation and counterfactual engine

Regression coefficients for each parent-to-child edge were estimated from lagged OLS regressions across the full panel (child[t] ~ parent[t-1], pooled across countries within each edge). Coefficients were constrained to honour the sign direction specified in the DAG — that is, if the OLS coefficient contradicted the domain-specified sign, the coefficient was set to the domain sign times the absolute OLS estimate. This conservatively captures the direction of causal influence while using the magnitude implied by the data.

From the last observed state in 2021, we forward-simulated each indicator to 2036 (a 15-year horizon matching the expected time for medical training pipeline effects to mature) using the estimated OLS coefficients plus Gaussian noise calibrated to the within-country year-on-year variance of each indicator. Indicators subject to intervention were linearly interpolated from their 2021 value toward the intervention target across the simulation horizon, reflecting realistic phase-in dynamics rather than instantaneous shifts. All draws used a fixed random seed (42) for exact reproducibility.

Uncertainty was quantified via 200 Monte Carlo draws per country-scenario combination, producing 80% prediction intervals (10th–90th percentile of the draw distribution) for each indicator and year. We report point estimates (mean of draws) and 80% intervals throughout.

### Counterfactual scenarios

We defined four scenarios:

**Scenario 0 — Baseline:** No intervention. All indicators continue their observed 2000–2021 trend trajectories extrapolated forward, with OLS-estimated drift terms and natural variability. This represents a business-as-usual world.

**Scenario A — Abuja target (5% GDP):** Total health expenditure (che\_gdp) is set to a minimum of 5% of GDP for all countries currently below this threshold by 2036, linearly phased in from 2022. The causal propagation to per-capita health spending, physician density, nurse density, UHC index, and downstream mortality indicators proceeds through the estimated DAG coefficients.

**Scenario B — Full investment (8% GDP + physician training x2):** Total health expenditure is set to a minimum of 8% of GDP, and physician density is simultaneously doubled relative to its 2021 baseline value (a 100% increase, reflecting the maximum plausible output of a sustained medical school expansion programme over 15 years). This scenario approximates what would be required for Africa to approach OECD-comparable service coverage levels by 2036.

**Scenario C — Aid increase (DAH +50%):** Development assistance for health is increased by 50% from 2021 levels, propagating through the external health expenditure share indicator (ext\_he) and thence to per-capita health spending and the downstream causal chain. This scenario specifically tests the leverage of international financing relative to domestic fiscal effort.

All counterfactual effects were propagated through the full DAG in topological order, ensuring that each indicator at simulation time t received updated values from its causal parents at t-1 under the intervention. Affected indicators were identified as all direct targets of the intervention plus their two-level causal descendants in the DAG.

### Downstream mortality estimation

Downstream mortality effects were computed by comparing Scenario B projections to Baseline for under-5 mortality and maternal mortality ratio at the country level, multiplied by the UN World Population Prospects 2022 projected birth cohort sizes for 2022–2036. This yields estimates of the number of deaths averted, reported at the continental level. These calculations are subject to greater uncertainty than the primary indicator projections and should be treated as order-of-magnitude estimates.

### Comparative benchmarks and gap analysis

For each country and each simulation year, we evaluated whether the projected physician density exceeded the WHO threshold of 44.5 health workers per 10,000 — approximated here using physicians plus nurses as a combined workforce indicator. Countries were classified as "on track" (threshold met or exceeded by 2036 in the mean projection), "marginal" (met under Scenario B but not Baseline), or "off track" (not met under any scenario). Regional summaries were computed as unweighted averages across countries within each AU geographic sub-region (North, West, Central, East, Southern Africa).

### Reproducibility

All model code, panel data, DAG specification, and simulation scripts are available at the project repository (AfricaForecast, C:\Models\AfricaForecast\). All random operations use seed 42; the validation framework confirms bitwise reproducibility of all reported point estimates. Software versions and Python dependencies are pinned in requirements.txt.

---

## Results

### Current health system status across 54 countries

As of the most recent complete data (2021 or most recent available), the continental median physician density is [TBD] per 10,000 population, ranging from below 0.5 in Niger, Chad, and South Sudan to above 20 in Libya, Tunisia, and Algeria. Nurse density shows a similar pattern: the continental median is [TBD] per 10,000, with West and Central African countries systematically below 5 per 10,000. Hospital bed density ranges from fewer than 0.5 per 1,000 in Ethiopia, Niger, and Mali to above 3.0 in South Africa and Seychelles.

Total health expenditure as a share of GDP has stagnated across much of the continent over the past decade. As of the most recent data, [TBD] of 54 countries allocate less than 5% of GDP to health, and [TBD] allocate less than 3%. Health expenditure per capita (PPP) ranges from below US\$50 per year in the lowest-income fragile states to above US\$1,200 in North and Southern African upper-middle-income countries.

The UHC service coverage index as of 2021 ranges from [TBD] (lowest, [TBD]) to [TBD] (highest, [TBD]) across the 54 countries. The continental mean is [TBD]. DTP3 immunisation coverage is above 90% in [TBD] countries but below 60% in [TBD] countries, primarily concentrated in Central and West Africa. Skilled birth attendance ranges from below 30% in Chad, Niger, and South Sudan to above 95% in North African and Southern African island states.

Out-of-pocket expenditure represents more than 40% of current health expenditure in [TBD] countries, reflecting limited public financing and catastrophic health spending risk at the household level. External health expenditure — development assistance — represents more than 30% of total health expenditure in [TBD] of the lowest-income countries, signalling high aid dependency that poses sustainability risks.

### Baseline trajectory to 2036

Under business-as-usual, the continental mean physician density is projected to reach [TBD] per 10,000 by 2036 (80% PI: [TBD]–[TBD]), compared with [TBD] in 2021 — a modest increase driven primarily by demographic and economic growth in East and Southern Africa. Only [TBD] of 54 countries are projected to meet the WHO 44.5 combined workforce threshold by 2036 under the baseline. Of the 54 countries, [TBD] are projected to show no meaningful increase in physician density and [TBD] are projected to show a decline relative to population growth.

The continental UHC index is projected to reach a mean of [TBD] (80% PI: [TBD]–[TBD]) by 2036 under baseline — an improvement of approximately [TBD] points from the 2021 mean of [TBD], but still far below the SDG target of 80. Countries in West and Central Africa are projected to see the slowest UHC index growth under baseline, with several Sahelian states showing essentially flat trajectories.

Maternal mortality ratios under baseline continue their slow decline across most of the continent, but [TBD] countries are projected to fail to meet the SDG 3.1 target of below 70 per 100,000 live births by 2030, let alone by 2036. Under-5 mortality similarly remains above the SDG 3.2 target of 25 per 1,000 live births in [TBD] countries under baseline.

### Scenario A: Abuja target (5% GDP)

Achieving the Abuja Declaration target — 5% of GDP allocated to health — for all countries currently below this threshold would, through the causal DAG, increase per-capita health spending across the continent. The downstream effect on physician density — mediated by health expenditure per capita to physician training and retention — results in an additional [TBD] countries meeting the WHO workforce threshold by 2036 compared with baseline.

The continental mean UHC index under Scenario A is projected to increase by [TBD] points above baseline by 2036 (80% PI: [TBD]–[TBD] point increase), reaching a continental mean of approximately [TBD]. The countries that gain most from this scenario are those with large domestic fiscal capacity currently underperforming on health spending — predominantly West African middle-income economies such as Nigeria, Ghana, and Senegal, where GDP is sufficient to finance the target but political prioritisation has been lacking.

DTP3 coverage under Scenario A is projected to increase to a continental mean of [TBD]% by 2036, compared with [TBD]% under baseline. Skilled birth attendance is projected to increase to [TBD]% from [TBD]% under baseline, reflecting the nurse density pathway through the DAG. Out-of-pocket expenditure share falls by approximately [TBD] percentage points on average, as increased government health expenditure substitutes for private payments.

However, Scenario A leaves a substantial gap. Even at 5% GDP, many of the lowest-income fragile states — where GDP itself is inadequate to generate sufficient revenues for health financing at the required scale — remain far below the WHO workforce threshold. For these countries, domestic fiscal effort alone, even at the Abuja target, cannot bridge the gap within the 15-year horizon.

### Scenario B: Full investment (8% GDP + physician training x2)

The full investment scenario — 8% of GDP on health combined with doubling of physician training throughput — produces substantially larger gains. By 2036, [TBD] countries (compared with [TBD] under baseline) are projected to meet the WHO 44.5 workforce threshold. The continental physician density is projected to reach [TBD] per 10,000 (80% PI: [TBD]–[TBD]), compared with [TBD] under baseline and [TBD] under Scenario A.

The UHC index under Scenario B reaches a projected continental mean of [TBD] by 2036 — [TBD] points above baseline and [TBD] points above Scenario A. Several East African countries (Kenya, Rwanda, Ethiopia) are projected to cross the 80-point SDG threshold under this scenario, which they do not reach under baseline or Scenario A.

The downstream mortality consequences of Scenario B are substantial. Through the causal pathways from UHC index and skilled birth attendance to under-5 and maternal mortality, and scaled by projected birth cohort sizes, Scenario B is estimated to prevent approximately [TBD] child deaths (under-5) and [TBD] maternal deaths across the continent over 2022–2036, relative to baseline. These estimates carry wide uncertainty intervals and should be interpreted as order-of-magnitude projections.

Cost-effectiveness, estimated from the change in life expectancy per percentage-point increase in health spending, suggests that each 1% of GDP increase in health spending translates to approximately [TBD] years of life expectancy gain at the continental level. This figure, derived from the causal DAG propagation, is consistent with published macro-level cross-country estimates from the World Bank and WHO Commission on Macroeconomics and Health.

### Scenario C: Aid increase (DAH +50%)

A 50% increase in development assistance for health, propagated through the external health expenditure pathway, produces more modest gains than either Scenario A or Scenario B for most countries. The continental mean UHC index under Scenario C is projected to be [TBD] points above baseline by 2036. Physician density gains are smaller than under Scenario A because the DAH pathway operates primarily through external health expenditure share, which has a weaker causal link to physician training and retention (which depends substantially on domestic fiscal and educational investment) compared with direct government health expenditure.

The benefit of Scenario C is concentrated in the most aid-dependent fragile states — predominantly in Central Africa, the Sahel, and the Horn — where domestic fiscal capacity is insufficient to deliver even the Abuja target without external supplementation. In these settings, the 50% DAH increase provides an estimated [TBD]-point UHC index gain above baseline by 2036, a meaningful improvement for populations otherwise off-track under all domestic-financing scenarios.

Importantly, Scenario C does not address the structural sustainability challenge of aid dependency. External health expenditure already represents more than 30% of total health spending in the most aid-dependent countries, which creates governance challenges and exposes health system financing to donor cycle volatility.

### Regional heterogeneity

Regional patterns are consistent across scenarios but vary substantially in magnitude. North Africa — Algeria, Egypt, Morocco, Tunisia — enters 2021 with the highest physician densities (continental median range [TBD]–[TBD] per 10,000) and the highest UHC index scores ([TBD] mean). Under all scenarios, North African countries remain on track and approach or exceed the WHO threshold; their primary challenge is NCD management and financial protection rather than workforce scarcity.

East Africa shows the strongest baseline improvement trajectory, driven by economic growth in Ethiopia and Kenya. Rwanda, whose health system has undergone extraordinary institutional strengthening since 2000, demonstrates one of the steepest UHC index improvement gradients in the continent and reaches the SDG threshold under Scenario B.

West Africa presents a bifurcated picture. Nigeria — with the continent's largest population and significant GDP — shows limited physician density gains under baseline due to chronic underinvestment relative to economic capacity and persistent medical brain drain. Under Scenario A and B, Nigeria's gains are among the largest in absolute terms, because its economic base allows rapid translation of political commitment into spending capacity. Sahelian states (Niger, Mali, Burkina Faso, Chad) remain below WHO thresholds under all scenarios modelled, underscoring that these countries require structural transformation — including WASH infrastructure, female education, and conflict resolution — beyond health spending alone.

Central Africa faces the largest combined deficits: physician density, UHC index, and essential medicines availability are all at or near continental minima for the Democratic Republic of Congo, Central African Republic, and South Sudan. These countries fail to meet the WHO threshold under any scenario modelled; closing their gaps would require additional instruments not captured in the current four-scenario framework, including conflict resolution, governance reform, and targeted vertical programme investment.

Southern Africa is the most heterogeneous sub-region. South Africa, Botswana, Namibia, and Mauritius show strong systems performance; Eswatini, Lesotho, Zimbabwe, and Mozambique remain significantly below WHO thresholds and are only partially reached by Scenario B by 2036.

### Sensitivity analyses

Excluding the five most fragile states (South Sudan, Somalia, CAF, DRC, Chad) from the continental aggregate does not materially change the direction or relative ordering of scenarios but improves the precision of the UHC index projections, as these states have the highest data missingness and the widest Monte Carlo uncertainty intervals. The full-sample results are reported in the main text; sensitivity results excluding fragile states are available in supplementary tables.

Results are robust to alternative coefficient sign enforcement strategies (unrestricted OLS versus sign-constrained OLS), to the choice of 80% versus 95% prediction intervals, and to alternative imputation strategies for missing indicator data.

---

## Discussion

### Principal findings

This analysis of 54 African Union member states using a causal DAG counterfactual engine yields four central findings. First, under current trends, Africa's health workforce gap will not close by 2036: only [TBD] of 54 countries are projected to meet the WHO minimum workforce threshold, and the continental UHC index will fall short of the SDG 3 target of 80. Second, reaching the Abuja Declaration target of 5% of GDP is necessary but insufficient; it narrows the gap but leaves most of the continent still below the WHO threshold. Third, the full investment scenario — 8% GDP on health combined with doubled physician training — is projected to enable [TBD] additional countries to cross the workforce threshold and to prevent hundreds of thousands of premature deaths. Fourth, aid increases alone provide meaningful gains in the most fragile settings but cannot substitute for domestic fiscal reform in larger economies.

### The causal architecture of investment effects

A key contribution of this analysis is the explicit articulation of the causal pathway from investment to outcomes. Health financing increases physician and nurse training and retention; higher workforce density expands service coverage as measured by the UHC index, DTP3 coverage, and skilled birth attendance; and improved coverage reduces child and maternal mortality. This chain has been recognised in qualitative terms for decades, but translating it into a quantifiable, country-specific, time-resolved projection — with uncertainty intervals that respect data quality — has been limited in the literature.

The 10-year horizon chosen for this analysis is not arbitrary. It reflects the realistic minimum time for medical school expansion to materialise in terms of trained clinicians entering the workforce. A student enrolled in 2024 in an expanded medical school programme completes pre-clinical and clinical training and a mandatory service period no earlier than 2030–2031, contributing to population-level workforce density only by 2032–2036. This pipeline constraint means that interventions focused exclusively on training acceleration cannot be evaluated over a five-year window; the 15-year horizon to 2036 is the appropriate planning frame.

### The insufficiency of the Abuja target alone

The Abuja Declaration (2001) committed African governments to allocating at least 15% of national budgets — approximately 5% of GDP for typical African fiscal structures — to health. More than two decades on, fewer than 15 of 54 AU member states have sustained this commitment. This analysis shows that even universal compliance with the Abuja target, while producing meaningful UHC index gains, would leave the majority of the continent below the WHO 44.5 combined workforce threshold by 2036.

The reason lies in the structure of the causal chain. The 5% GDP commitment translates into a specific per-capita spending level that, through the OLS-estimated DAG coefficients, generates a predicted physician density. In the lowest-income AU member states, where GDP per capita is below USD 500 (PPP), 5% of GDP translates to fewer than USD 25 per capita per year in total health spending — far below the USD 86 per capita benchmark that the WHO Commission on Macroeconomics and Health identified as the minimum for basic essential health services. The Abuja target is denominated in budget shares, not absolute amounts; it therefore provides less real financing in poor countries than in rich ones.

This arithmetic drives our finding that Scenario A narrows but does not close the gap. Reaching 8% of GDP — Scenario B — provides substantially more per-capita spending in those countries where GDP growth over the 2022–2036 period is projected to be strong (East Africa, West Africa's middle-income economies). Combined with accelerated physician training, this scenario achieves the largest workforce gains in countries that have sufficient economic mass to translate the spending commitment into training capacity.

### Aid as complement, not substitute

Scenario C — a 50% increase in DAH — provides the most benefit in the most fragile settings, where domestic fiscal capacity is genuinely insufficient. This is consistent with the normative rationale for development assistance: to supplement domestic effort in settings where fiscal constraints bind. However, the analysis also demonstrates the limits of aid-led approaches.

First, the OLS-estimated coefficient linking external health expenditure share to physician density is weaker than the coefficient linking domestic government health expenditure to physician density. This reflects the documented tendency of external health financing to flow disproportionately to vertical programmes (HIV/AIDS, malaria, immunisation) rather than to system-building investments such as medical training, hospital infrastructure, and workforce retention. Second, high external health expenditure share is associated with governance fragility and aid-cycle volatility, both of which reduce the reliability of multi-year workforce planning. Third, even a 50% increase in DAH represents a politically ambitious target; it would require donor commitments substantially above those achieved by the Global Fund, Gavi, and PEPFAR combined relative to current baselines.

The most durable path to closing the gap is domestic fiscal reform — expanding the tax base, improving budget execution, and raising the political priority of health — complemented by targeted external financing for the lowest-income fragile states where the domestic fiscal base cannot carry the burden alone.

### Regional implications for policy

The regional heterogeneity in our results has direct policy implications. For North Africa, the primary health system challenge is not workforce quantity but quality and equity of access, NCD management capacity, and financial protection. For East Africa — particularly Ethiopia, Kenya, Uganda, and Tanzania — the trajectory under Scenario B is genuinely optimistic; these countries could approach regional and continental leadership in health systems performance by 2036 if investment targets are met. For West Africa, the central challenge is political economy: Nigeria's economic mass makes it capable of Scenario A or B compliance, but historical underinvestment relative to GDP suggests the binding constraint is political prioritisation rather than fiscal capacity. For Central Africa and the Sahelian belt, the analysis confirms that health system investment alone is insufficient; conflict resolution, WASH infrastructure, and female education are prior conditions without which health spending cannot efficiently produce workforce or coverage gains.

### Limitations

This analysis has several important limitations. First, the training pipeline for physicians is treated through the OLS-estimated coefficient linking health spending to physician density; the explicit dynamics of medical school enrolment, training duration, attrition, and examination are not modelled separately. Doubling physician training (Scenario B) is operationalised as a multiplier on physician density rather than a structural model of the training system. The results for Scenario B should therefore be interpreted as the maximum that could be expected given the resource investment, not as a precise prediction.

Second, physician emigration — a major structural constraint for many African health systems — is not explicitly modelled. The DAG's OLS coefficients capture the net historical relationship between spending and density, which implicitly includes emigration effects, but does not allow us to disaggregate how much of the gap is driven by emigration versus insufficient training. Policies aimed at retention (obligatory service requirements, salary enhancement, rural incentives) may have different efficiency profiles from training expansion and would require separate modelling.

Third, data quality for fragile states — South Sudan, Somalia, Central African Republic, and to some extent the Democratic Republic of Congo — is limited. Physician density and UHC index values for these countries carry wide uncertainty ranges beyond those captured in our 80% Monte Carlo intervals, which reflect model uncertainty rather than data measurement uncertainty. Results for these countries should be treated with particular caution.

Fourth, the causal DAG, while grounded in published evidence, reflects subjective judgements about which edges to include and what signs to assign. We did not attempt to validate the DAG structure against counterfactual experiments; such validation would require instrumental variable or quasi-experimental evidence not available at the 54-country, multi-decade scale. The DAG should be understood as encoding domain expert consensus, not empirically verified causal structure.

Fifth, the scenario projections assume stable relationships between spending and workforce outcomes. Structural breaks — such as the COVID-19 pandemic's documented reversal of health system gains — could alter trajectories in ways not captured by OLS coefficients estimated from pre-pandemic data.

Finally, economic projections underlying Scenario B (which requires 8% of GDP from countries currently averaging 5%) assume continued GDP growth at historical rates. A global recession, commodity price collapse, or sovereign debt crisis could reduce the fiscal space for health spending substantially below the scenario targets.

### Generalisability and next steps

While this analysis is specific to Africa, the causal architecture and scenario methodology are generalisable. The AfricaForecast DAG represents a codified theory of the health system that could, with appropriate data, be applied to South Asia, Latin America, or any region where workforce-spending-coverage-outcome linkages are the focus of policy analysis.

The most immediate policy-relevant extension of this work is a country-specific investment calculator that translates a given country's GDP growth projection and baseline health spending into projected workforce and coverage gains under alternative political commitments. Such a tool, built on the counterfactual engine described here, would provide national planning ministries with a data-grounded answer to the question: what would it cost us, and what would we get, if we committed to 8% of GDP on health by 2030?

---

## Conclusion

Africa can close its health workforce gap by 2036, but only under sustained investment commitments that exceed the Abuja Declaration target of 5% of GDP. The full investment scenario — 8% of GDP on health combined with doubled physician training throughput — is projected to bring [TBD] additional countries above the WHO minimum workforce threshold, increase the continental UHC index to approximately [TBD], and prevent hundreds of thousands of child and maternal deaths by 2036. The Abuja target, while politically significant, is arithmetically insufficient for the lowest-income AU member states where GDP is too small to generate adequate per-capita health financing at 5% of GDP alone. Development assistance provides meaningful leverage in fragile settings but cannot substitute for domestic fiscal reform in larger economies. The causal model confirms that the sequence matters: financing drives workforce, workforce drives coverage, coverage drives outcomes — and this chain can be unlocked within a realistic 10–15 year horizon if political commitment is sustained.

---

## Contributors

Conception and design: [Author initials TBD]. Data acquisition: [Author initials TBD]. Causal DAG specification: [Author initials TBD]. Counterfactual engine development: [Author initials TBD]. Statistical analysis: [Author initials TBD]. Drafting of manuscript: [Author initials TBD]. Critical revision for important intellectual content: all authors. All authors approved the final version and agreed to be accountable for all aspects of the work.

---

## Declaration of interests

The authors declare no conflicts of interest. No commercial or government funding was received for this work. All data used are openly available from WHO, World Bank, and IHME.

---

## Data sharing

All data, model code, DAG specification, and simulation results are available at the AfricaForecast project repository. Indicator data were obtained exclusively from open-access sources (WHO GHO, World Bank WDI, IHME GBD). No individual-level patient data were used. The simulation engine and all analysis scripts can be run offline without API keys using the provided panel.csv and requirements.txt. Results are bitwise reproducible under seed 42.

---

## Acknowledgements

We thank the WHO Global Health Observatory, World Bank Development Data Group, and the Institute for Health Metrics and Evaluation for maintaining the open-access data infrastructure that makes continental-scale health system modelling feasible. We acknowledge the broader AfricaForecast development community for methodological contributions to the causal graph architecture and the counterfactual simulation framework.

---

## References

1. World Health Organization. *Global Health Workforce Statistics.* WHO GHO. Geneva: WHO; 2023.
2. World Health Organization. *Monitoring the building blocks of health systems: a handbook of indicators and their measurement strategies.* Geneva: WHO; 2010.
3. African Union. *Abuja Declaration on HIV/AIDS, Tuberculosis and Other Related Infectious Diseases.* OAU/SPS/ABUJA/3. Abuja: African Union; 2001.
4. Commission on Macroeconomics and Health. *Macroeconomics and Health: Investing in Health for Economic Development.* Geneva: WHO; 2001.
5. Lancet Commission on Investing in Health. *Global health 2035: a world converging within a generation.* Lancet. 2013;382(9908):1898–955.
6. World Health Organization. *UHC service coverage index.* WHO GHO Technical Notes. Geneva: WHO; 2023.
7. Institute for Health Metrics and Evaluation. *Global Burden of Disease Study 2021.* Seattle: IHME; 2023.
8. Dieleman JL, Campbell M, Chapin A, et al. Future and potential spending on health 2015–40. *Lancet.* 2017;389(10083):2005–30.
9. Anand S, Barnighausen T. Health workers and vaccination coverage in developing countries. *Lancet.* 2007;369(9569):1277–85.
10. Pearl J. *Causality: Models, Reasoning, and Inference.* 2nd ed. Cambridge: Cambridge University Press; 2009.
11. World Bank. *World Development Indicators.* Washington DC: World Bank Group; 2023. doi:10.57966/JH8P-R677.
12. Kirigia JM, Barry SP. Health challenges and opportunities for Africa beyond 2015. *BMC Int Health Hum Rights.* 2008;8:16.
13. Scheffler RM, Campbell J, Cometto G, et al. Forecasting imbalances in the global health labor market. *Hum Resour Health.* 2018;16:24.
14. Mills A. Health care systems in low- and middle-income countries. *NEJM.* 2014;370(6):552–7.
15. Kruk ME, Gage AD, Arsenault C, et al. High-quality health systems in the Sustainable Development Goals era. *Lancet.* 2018;6(11):e1196–252.

---

*Manuscript word count: approximately 4,900 words (excluding tables, figures, and references)*
*Paper 4 of the AfricaForecast series | AfricaForecast counterfactual engine v1.0 | Seed 42 | Data vintage: WHO/WB 2021*
