# Earth Whisper - Step 10A Candidate Investigations

Project: Earth Whisper
AOI: Sandhya River near Babuganj, Barishal, Bangladesh
Investigation date: 2026-09-25
Candidates investigated: 32

Selection rule: top 20 candidates by comparison_aware_anomaly_percentile (cutoff 0.914530) union all candidates whose cross_radar_status is dual_radar_upper_quartile_stable or dual_radar_upper_quartile_but_sensitive, de-duplicated by candidate_key. No other ranking criterion was used.

Standing limitations carried from Step 9 (verbatim source statements):
- L01 (NISAR_measurement, documented): NISAR GUNW observations are interferometric measurements over specific acquisition pairs.
- L02 (temporal_baseline, documented): The selected NISAR comparisons have different temporal intervals and do not form one uniform temporal baseline.
- L03 (polarization, implemented): The selected NISAR GUNWs include both HH and VV measurements.
- L04 (Sentinel1_crosscheck, documented): Sentinel-1 measurements were sampled around candidates that were already identified from NISAR.
- L05 (optical_verification, implemented): Only six candidate regions received detailed optical verification.
- L06 (optical_quality, implemented): The tested optical observations were dominated by high-aerosol conditions and had no valid pixels for the verification calculation.
- L07 (rainfall_context, implemented): GPM IMERG rainfall has substantially coarser spatial resolution than the Sandhya AOI and candidate regions.
- L08 (rainfall_availability, documented): The full 14-day rainfall window was unavailable for the GUNW_023 context date.
- L09 (candidate_selection, documented): The 211 records are candidates selected from NISAR change detection rather than an unbiased sample of all locations in the AOI.
- L10 (ML_anomaly_detection, implemented): The kNN model is unsupervised and identifies statistical isolation in the selected Sentinel-1 feature space.
- L11 (ML_sensitivity, implemented): Anomaly results can vary with neighbourhood size, with a subset of candidates showing higher k-sensitivity.
- L12 (comparison_population, implemented): The HH comparison contains 195 candidates while the VV comparison contains only 16 candidates.
- L13 (ground_truth, documented): No independent ground-truth labels are currently available for confirmed erosion, deposition, landslide, or other physical events.
- L14 (physical_interpretation, documented): Radar coherence or backscatter changes can have multiple physical and environmental causes.
- L15 (confidence_claims, implemented): The current evidence layers do not support a calibrated physical-event probability.

Every value below is copied from the Step 6-9 source tables. Rainfall is AOI-level context and is not a spatial discriminator. No event probability or confirmed physical-event label is produced.

---

Candidate:
Candidate key: HH_023_to_029_265
Comparison: HH_023_to_029
Region: 265

Location: lon 90.2193002, lat 22.5057964
Area: 5200 m2

NISAR observation: change=-0.3435297310352325, change_strength=0.3435297310352325, signal_percentile=0.8564102564102564, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.6176549792289734; GUNW_023_HH_mean=0.6188307404518127; GUNW_029_HH_median=0.2741252481937408; GUNW_029_HH_mean=0.303368866443634; HH_023_to_029_change=-0.3435297310352325
Sentinel-1 observation: s1_median_db=-6.784132957458496, s1_min_db=-13.665271759033203, s1_max_db=8.233678817749023, s1_pct_le_minus3db=75.6923076923077; comparison-aware anomaly percentile=1.0 (kNN stability percentile 0.9984202211690363, high_sensitivity); cross_radar_status=dual_radar_upper_quartile_but_sensitive
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k)
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3435297310352325 (band upper_quartile, percentile 0.8564102564102564); Sentinel-1 comparison-aware anomaly percentile 1.0; cross-radar: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k); optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: A multi-radar signal in which both radar sources are upper-quartile for their comparison population, but the anomaly position moves with neighbourhood size. This merits further investigation with explicit attention to k-sensitivity.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1786
Comparison: HH_023_to_029
Region: 1786

Location: lon 90.1647003, lat 22.4790948
Area: 4400 m2

NISAR observation: change=-0.3076928555965423, change_strength=0.3076928555965423, signal_percentile=0.6, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.6266696453094482; GUNW_023_HH_mean=0.6520923972129822; GUNW_029_HH_median=0.3189767897129059; GUNW_029_HH_mean=0.3425018191337585; HH_023_to_029_change=-0.3076928555965423
Sentinel-1 observation: s1_median_db=-7.877784729003906, s1_min_db=-17.871479034423828, s1_max_db=4.050341606140137, s1_pct_le_minus3db=77.45454545454545; comparison-aware anomaly percentile=0.9914529914529915 (kNN stability percentile 0.9968404423380726, high_sensitivity); cross_radar_status=s1_upper_quartile_but_sensitive
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k)
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3076928555965423 (band middle_half, percentile 0.6); Sentinel-1 comparison-aware anomaly percentile 0.9914529914529915; cross-radar: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k); optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_296
Comparison: HH_023_to_029
Region: 296

Location: lon 90.1965035, lat 22.5039642
Area: 19600 m2

NISAR observation: change=-0.3083744049072265, change_strength=0.3083744049072265, signal_percentile=0.6102564102564103, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.627459704875946; GUNW_023_HH_mean=0.6178386807441711; GUNW_029_HH_median=0.3190852999687195; GUNW_029_HH_mean=0.3146906793117523; HH_023_to_029_change=-0.3083744049072265
Sentinel-1 observation: s1_median_db=-4.002299785614014, s1_min_db=-19.77579498291016, s1_max_db=7.239642143249512, s1_pct_le_minus3db=54.285714285714285; comparison-aware anomaly percentile=0.9897435897435898 (kNN stability percentile 0.9810426540284359, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3083744049072265 (band middle_half, percentile 0.6102564102564103); Sentinel-1 comparison-aware anomaly percentile 0.9897435897435898; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_478
Comparison: HH_023_to_029
Region: 478

Location: lon 90.1545898, lat 22.4993345
Area: 25600 m2

NISAR observation: change=-0.2930508255958557, change_strength=0.2930508255958557, signal_percentile=0.38974358974358975, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.5766341090202332; GUNW_023_HH_mean=0.5739877223968506; GUNW_029_HH_median=0.2835832834243774; GUNW_029_HH_mean=0.2828402519226074; HH_023_to_029_change=-0.2930508255958557
Sentinel-1 observation: s1_median_db=-0.373748242855072, s1_min_db=-18.87372398376465, s1_max_db=9.23316478729248, s1_pct_le_minus3db=21.25; comparison-aware anomaly percentile=0.9863247863247864 (kNN stability percentile 0.9731437598736177, low_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2930508255958557 (band lower_half, percentile 0.38974358974358975); Sentinel-1 comparison-aware anomaly percentile 0.9863247863247864; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_167
Comparison: HH_023_to_029
Region: 167

Location: lon 90.164763, lat 22.5061629
Area: 4000 m2

NISAR observation: change=-0.2980999052524566, change_strength=0.2980999052524566, signal_percentile=0.46153846153846156, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.5960484743118286; GUNW_023_HH_mean=0.5882750749588013; GUNW_029_HH_median=0.2979485690593719; GUNW_029_HH_mean=0.3001316785812378; HH_023_to_029_change=-0.2980999052524566
Sentinel-1 observation: s1_median_db=-3.8508901596069336, s1_min_db=-20.17854690551757, s1_max_db=2.612679004669189, s1_pct_le_minus3db=60.0; comparison-aware anomaly percentile=0.9811965811965813 (kNN stability percentile 0.9873617693522907, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2980999052524566 (band lower_half, percentile 0.46153846153846156); Sentinel-1 comparison-aware anomaly percentile 0.9811965811965813; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_246
Comparison: HH_023_to_029
Region: 246

Location: lon 90.1515533, lat 22.5042809
Area: 7200 m2

NISAR observation: change=-0.3234554529190063, change_strength=0.3234554529190063, signal_percentile=0.7282051282051282, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.5975152254104614; GUNW_023_HH_mean=0.608715295791626; GUNW_029_HH_median=0.2740597724914551; GUNW_029_HH_mean=0.2644229829311371; HH_023_to_029_change=-0.3234554529190063
Sentinel-1 observation: s1_median_db=-6.266297340393066, s1_min_db=-15.668298721313477, s1_max_db=5.712562561035156, s1_pct_le_minus3db=70.44444444444444; comparison-aware anomaly percentile=0.9743589743589743 (kNN stability percentile 0.971563981042654, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3234554529190063 (band middle_half, percentile 0.7282051282051282); Sentinel-1 comparison-aware anomaly percentile 0.9743589743589743; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_188
Comparison: HH_023_to_029
Region: 188

Location: lon 90.1662475, lat 22.5055933
Area: 8400 m2

NISAR observation: change=-0.3361970782279968, change_strength=0.3361970782279968, signal_percentile=0.8102564102564103, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5603159666061401; GUNW_023_HH_mean=0.5538536310195923; GUNW_029_HH_median=0.2241188883781433; GUNW_029_HH_mean=0.2359091490507125; HH_023_to_029_change=-0.3361970782279968
Sentinel-1 observation: s1_median_db=-5.094924449920654, s1_min_db=-15.804698944091797, s1_max_db=1.217437505722046, s1_pct_le_minus3db=72.19047619047619; comparison-aware anomaly percentile=0.9675213675213675 (kNN stability percentile 0.9731437598736177, high_sensitivity); cross_radar_status=dual_radar_upper_quartile_but_sensitive
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k)
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3361970782279968 (band upper_quartile, percentile 0.8102564102564103); Sentinel-1 comparison-aware anomaly percentile 0.9675213675213675; cross-radar: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k); optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: A multi-radar signal in which both radar sources are upper-quartile for their comparison population, but the anomaly position moves with neighbourhood size. This merits further investigation with explicit attention to k-sensitivity.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_970
Comparison: HH_023_to_029
Region: 970

Location: lon 90.1977177, lat 22.4930461
Area: 7200 m2

NISAR observation: change=-0.2730003893375397, change_strength=0.2730003893375397, signal_percentile=0.20512820512820512, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.5527639389038086; GUNW_023_HH_mean=0.5684707164764404; GUNW_029_HH_median=0.2797635495662689; GUNW_029_HH_mean=0.2688494920730591; HH_023_to_029_change=-0.2730003893375397
Sentinel-1 observation: s1_median_db=-5.619558334350586, s1_min_db=-13.863091468811035, s1_max_db=2.148240566253662, s1_pct_le_minus3db=78.0; comparison-aware anomaly percentile=0.9606837606837607 (kNN stability percentile 0.9636650868878357, high_sensitivity); cross_radar_status=s1_upper_quartile_but_sensitive
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k)
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2730003893375397 (band lower_half, percentile 0.20512820512820512); Sentinel-1 comparison-aware anomaly percentile 0.9606837606837607; cross-radar: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k); optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_224
Comparison: HH_023_to_029
Region: 224

Location: lon 90.2040889, lat 22.5062164
Area: 5600 m2

NISAR observation: change=-0.2983033359050751, change_strength=0.2983033359050751, signal_percentile=0.4717948717948718, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.5138936042785645; GUNW_023_HH_mean=0.5112362504005432; GUNW_029_HH_median=0.2155902683734893; GUNW_029_HH_mean=0.2177038937807083; HH_023_to_029_change=-0.2983033359050751
Sentinel-1 observation: s1_median_db=-2.718303680419922, s1_min_db=-7.505241394042969, s1_max_db=3.180537462234497, s1_pct_le_minus3db=45.14285714285714; comparison-aware anomaly percentile=0.9572649572649573 (kNN stability percentile 0.9462875197472354, low_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2983033359050751 (band lower_half, percentile 0.4717948717948718); Sentinel-1 comparison-aware anomaly percentile 0.9572649572649573; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_2020
Comparison: HH_023_to_029
Region: 2020

Location: lon 90.211825, lat 22.47588
Area: 4000 m2

NISAR observation: change=-0.273408979177475, change_strength=0.273408979177475, signal_percentile=0.21025641025641026, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.4691968262195587; GUNW_023_HH_mean=0.4708961546421051; GUNW_029_HH_median=0.1957878470420837; GUNW_029_HH_mean=0.2060928642749786; HH_023_to_029_change=-0.273408979177475
Sentinel-1 observation: s1_median_db=0.4654226303100586, s1_min_db=-11.120553016662598, s1_max_db=11.774128913879396, s1_pct_le_minus3db=23.200000000000003; comparison-aware anomaly percentile=0.9504273504273505 (kNN stability percentile 0.9541864139020536, low_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.273408979177475 (band lower_half, percentile 0.21025641025641026); Sentinel-1 comparison-aware anomaly percentile 0.9504273504273505; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_900
Comparison: HH_023_to_029
Region: 900

Location: lon 90.1970033, lat 22.4942171
Area: 4000 m2

NISAR observation: change=-0.3422118127346039, change_strength=0.3422118127346039, signal_percentile=0.841025641025641, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5607460737228394; GUNW_023_HH_mean=0.5613484978675842; GUNW_029_HH_median=0.2185342609882354; GUNW_029_HH_mean=0.1950148344039917; HH_023_to_029_change=-0.3422118127346039
Sentinel-1 observation: s1_median_db=-4.627696514129639, s1_min_db=-12.340471267700195, s1_max_db=2.5861587524414062, s1_pct_le_minus3db=66.4; comparison-aware anomaly percentile=0.9487179487179488 (kNN stability percentile 0.9526066350710901, high_sensitivity); cross_radar_status=dual_radar_upper_quartile_but_sensitive
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3422118127346039 (band upper_quartile, percentile 0.841025641025641); Sentinel-1 comparison-aware anomaly percentile 0.9487179487179488; cross-radar: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: A multi-radar signal in which both radar sources are upper-quartile for their comparison population, but the anomaly position moves with neighbourhood size. This merits further investigation with explicit attention to k-sensitivity.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1536
Comparison: HH_023_to_029
Region: 1536

Location: lon 90.1976151, lat 22.4835072
Area: 5200 m2

NISAR observation: change=-0.2585837543010711, change_strength=0.2585837543010711, signal_percentile=0.13333333333333333, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.6171997785568237; GUNW_023_HH_mean=0.6292436122894287; GUNW_029_HH_median=0.3586160242557525; GUNW_029_HH_mean=0.3588197827339172; HH_023_to_029_change=-0.2585837543010711
Sentinel-1 observation: s1_median_db=-3.917623519897461, s1_min_db=-11.38877010345459, s1_max_db=3.6618974208831774, s1_pct_le_minus3db=58.15384615384615; comparison-aware anomaly percentile=0.9452991452991452 (kNN stability percentile 0.9399684044233808, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2585837543010711 (band lower_half, percentile 0.13333333333333333); Sentinel-1 comparison-aware anomaly percentile 0.9452991452991452; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_2186
Comparison: HH_023_to_029
Region: 2186

Location: lon 90.2035156, lat 22.4728267
Area: 10400 m2

NISAR observation: change=-0.3152260780334472, change_strength=0.3152260780334472, signal_percentile=0.6666666666666666, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.5793720483779907; GUNW_023_HH_mean=0.5977466106414795; GUNW_029_HH_median=0.2641459703445434; GUNW_029_HH_mean=0.2785446643829345; HH_023_to_029_change=-0.3152260780334472
Sentinel-1 observation: s1_median_db=1.0551341772079468, s1_min_db=-6.8948893547058105, s1_max_db=12.47174072265625, s1_pct_le_minus3db=6.0; comparison-aware anomaly percentile=0.9452991452991452 (kNN stability percentile 0.9478672985781991, low_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3152260780334472 (band middle_half, percentile 0.6666666666666666); Sentinel-1 comparison-aware anomaly percentile 0.9452991452991452; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1628
Comparison: HH_023_to_029
Region: 1628

Location: lon 90.1614775, lat 22.4815178
Area: 4000 m2

NISAR observation: change=-0.3165184259414673, change_strength=0.3165184259414673, signal_percentile=0.6923076923076923, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.6107136607170105; GUNW_023_HH_mean=0.6226144433021545; GUNW_029_HH_median=0.2941952347755432; GUNW_029_HH_mean=0.3073760569095611; HH_023_to_029_change=-0.3165184259414673
Sentinel-1 observation: s1_median_db=-0.4454201459884643, s1_min_db=-12.505743026733398, s1_max_db=3.4912915229797363, s1_pct_le_minus3db=14.000000000000002; comparison-aware anomaly percentile=0.9333333333333332 (kNN stability percentile 0.919431279620853, low_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3165184259414673 (band middle_half, percentile 0.6923076923076923); Sentinel-1 comparison-aware anomaly percentile 0.9333333333333332; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1653
Comparison: HH_023_to_029
Region: 1653

Location: lon 90.1711812, lat 22.4810025
Area: 4000 m2

NISAR observation: change=-0.2763198018074035, change_strength=0.2763198018074035, signal_percentile=0.24102564102564103, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.4507311582565307; GUNW_023_HH_mean=0.4697547852993011; GUNW_029_HH_median=0.1744113564491272; GUNW_029_HH_mean=0.2085823565721511; HH_023_to_029_change=-0.2763198018074035
Sentinel-1 observation: s1_median_db=-2.257699966430664, s1_min_db=-11.97625732421875, s1_max_db=2.5054714679718018, s1_pct_le_minus3db=32.4; comparison-aware anomaly percentile=0.9264957264957264 (kNN stability percentile 0.9273301737756713, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2763198018074035 (band lower_half, percentile 0.24102564102564103); Sentinel-1 comparison-aware anomaly percentile 0.9264957264957264; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1933
Comparison: HH_023_to_029
Region: 1933

Location: lon 90.1553133, lat 22.4761281
Area: 5200 m2

NISAR observation: change=-0.3066991418600082, change_strength=0.3066991418600082, signal_percentile=0.5897435897435898, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.5552476644515991; GUNW_023_HH_mean=0.5688583850860596; GUNW_029_HH_median=0.2485485225915908; GUNW_029_HH_mean=0.2717608511447906; HH_023_to_029_change=-0.3066991418600082
Sentinel-1 observation: s1_median_db=-2.876049041748047, s1_min_db=-16.520580291748047, s1_max_db=4.2673420906066895, s1_pct_le_minus3db=46.15384615384615; comparison-aware anomaly percentile=0.9196581196581196 (kNN stability percentile 0.9162717219589257, high_sensitivity); cross_radar_status=s1_upper_quartile_but_sensitive
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3066991418600082 (band middle_half, percentile 0.5897435897435898); Sentinel-1 comparison-aware anomaly percentile 0.9196581196581196; cross-radar: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_53
Comparison: HH_023_to_029
Region: 53

Location: lon 90.1616915, lat 22.5084431
Area: 5200 m2

NISAR observation: change=-0.3040426075458526, change_strength=0.3040426075458526, signal_percentile=0.5333333333333333, signal_band=middle_half; coherence measurements: GUNW_023_HH_median=0.5828549861907959; GUNW_023_HH_mean=0.5655262470245361; GUNW_029_HH_median=0.2788123786449432; GUNW_029_HH_mean=0.2672613561153412; HH_023_to_029_change=-0.3040426075458526
Sentinel-1 observation: s1_median_db=-0.6715005040168762, s1_min_db=-11.627962112426758, s1_max_db=9.95526885986328, s1_pct_le_minus3db=23.07692307692308; comparison-aware anomaly percentile=0.9179487179487179 (kNN stability percentile 0.9083728278041073, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3040426075458526 (band middle_half, percentile 0.5333333333333333); Sentinel-1 comparison-aware anomaly percentile 0.9179487179487179; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_608
Comparison: HH_023_to_029
Region: 608

Location: lon 90.2138264, lat 22.4992722
Area: 5200 m2

NISAR observation: change=-0.2401995509862899, change_strength=0.2401995509862899, signal_percentile=0.03076923076923077, signal_band=lower_half; coherence measurements: GUNW_023_HH_median=0.4513066112995147; GUNW_023_HH_mean=0.4572688639163971; GUNW_029_HH_median=0.2111070603132248; GUNW_029_HH_mean=0.1987609565258026; HH_023_to_029_change=-0.2401995509862899
Sentinel-1 observation: s1_median_db=-3.506811618804932, s1_min_db=-9.186506271362305, s1_max_db=6.525031089782715, s1_pct_le_minus3db=55.38461538461539; comparison-aware anomaly percentile=0.9145299145299145 (kNN stability percentile 0.9210110584518167, moderate_sensitivity); cross_radar_status=s1_upper_quartile_nisar_not_upper_quartile
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.2401995509862899 (band lower_half, percentile 0.03076923076923077); Sentinel-1 comparison-aware anomaly percentile 0.9145299145299145; cross-radar: only the Sentinel-1 anomaly is upper-quartile; the NISAR measurement is not upper-quartile; optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1145
Comparison: HH_023_to_029
Region: 1145

Location: lon 90.1535976, lat 22.4889715
Area: 10000 m2

NISAR observation: change=-0.3406970947980881, change_strength=0.3406970947980881, signal_percentile=0.8256410256410256, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5129606127738953; GUNW_023_HH_mean=0.5346900224685669; GUNW_029_HH_median=0.1722635179758072; GUNW_029_HH_mean=0.2084358185529709; HH_023_to_029_change=-0.3406970947980881
Sentinel-1 observation: s1_median_db=-0.2568335235118866, s1_min_db=-12.025924682617188, s1_max_db=7.998111248016357, s1_pct_le_minus3db=31.2; comparison-aware anomaly percentile=0.9094017094017094 (kNN stability percentile 0.8783570300157978, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3406970947980881 (band upper_quartile, percentile 0.8256410256410256); Sentinel-1 comparison-aware anomaly percentile 0.9094017094017094; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_982
Comparison: HH_023_to_029
Region: 982

Location: lon 90.2163498, lat 22.4930107
Area: 9600 m2

NISAR observation: change=-0.3484015464782715, change_strength=0.3484015464782715, signal_percentile=0.8923076923076924, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5853420495986938; GUNW_023_HH_mean=0.576382577419281; GUNW_029_HH_median=0.2369405031204223; GUNW_029_HH_mean=0.2412420064210891; HH_023_to_029_change=-0.3484015464782715
Sentinel-1 observation: s1_median_db=-1.5974197387695312, s1_min_db=-14.267704010009766, s1_max_db=5.852346897125244, s1_pct_le_minus3db=35.833333333333336; comparison-aware anomaly percentile=0.888888888888889 (kNN stability percentile 0.8704581358609795, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3484015464782715 (band upper_quartile, percentile 0.8923076923076924); Sentinel-1 comparison-aware anomaly percentile 0.888888888888889; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1902
Comparison: HH_023_to_029
Region: 1902

Location: lon 90.1744236, lat 22.4772594
Area: 4800 m2

NISAR observation: change=-0.4943587481975555, change_strength=0.4943587481975555, signal_percentile=1.0, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.6748321652412415; GUNW_023_HH_mean=0.674978494644165; GUNW_029_HH_median=0.1804734170436859; GUNW_029_HH_mean=0.2036920636892318; HH_023_to_029_change=-0.4943587481975555
Sentinel-1 observation: s1_median_db=-2.630305290222168, s1_min_db=-9.480363845825195, s1_max_db=7.744106292724609, s1_pct_le_minus3db=47.66666666666667; comparison-aware anomaly percentile=0.8803418803418803 (kNN stability percentile 0.8736176935229069, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.4943587481975555 (band upper_quartile, percentile 1.0); Sentinel-1 comparison-aware anomaly percentile 0.8803418803418803; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1640
Comparison: HH_023_to_029
Region: 1640

Location: lon 90.2182324, lat 22.4821097
Area: 7600 m2

NISAR observation: change=-0.3769729435443878, change_strength=0.3769729435443878, signal_percentile=0.9487179487179487, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.7020473480224609; GUNW_023_HH_mean=0.6869997382164001; GUNW_029_HH_median=0.3250744044780731; GUNW_029_HH_mean=0.365148663520813; HH_023_to_029_change=-0.3769729435443878
Sentinel-1 observation: s1_median_db=1.9021246433258057, s1_min_db=-9.72054958343506, s1_max_db=9.038954734802246, s1_pct_le_minus3db=8.842105263157894; comparison-aware anomaly percentile=0.8752136752136752 (kNN stability percentile 0.8704581358609794, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3769729435443878 (band upper_quartile, percentile 0.9487179487179487); Sentinel-1 comparison-aware anomaly percentile 0.8752136752136752; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_2035
Comparison: HH_023_to_029
Region: 2035

Location: lon 90.2064473, lat 22.4757267
Area: 6000 m2

NISAR observation: change=-0.3833246082067489, change_strength=0.3833246082067489, signal_percentile=0.9641025641025641, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.6186333894729614; GUNW_023_HH_mean=0.587833821773529; GUNW_029_HH_median=0.2353087812662124; GUNW_029_HH_mean=0.2481728196144104; HH_023_to_029_change=-0.3833246082067489
Sentinel-1 observation: s1_median_db=-1.6865010261535645, s1_min_db=-10.99680519104004, s1_max_db=3.365264415740967, s1_pct_le_minus3db=33.86666666666667; comparison-aware anomaly percentile=0.8495726495726497 (kNN stability percentile 0.8436018957345972, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3833246082067489 (band upper_quartile, percentile 0.9641025641025641); Sentinel-1 comparison-aware anomaly percentile 0.8495726495726497; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1980
Comparison: HH_023_to_029
Region: 1980

Location: lon 90.1607959, lat 22.4749889
Area: 7600 m2

NISAR observation: change=-0.3316811323165893, change_strength=0.3316811323165893, signal_percentile=0.7794871794871795, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.547349214553833; GUNW_023_HH_mean=0.538489818572998; GUNW_029_HH_median=0.2156680822372436; GUNW_029_HH_mean=0.2330350428819656; HH_023_to_029_change=-0.3316811323165893
Sentinel-1 observation: s1_median_db=-0.7313910722732544, s1_min_db=-10.883277893066406, s1_max_db=7.908244132995605, s1_pct_le_minus3db=36.63157894736842; comparison-aware anomaly percentile=0.8478632478632478 (kNN stability percentile 0.8325434439178515, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3316811323165893 (band upper_quartile, percentile 0.7794871794871795); Sentinel-1 comparison-aware anomaly percentile 0.8478632478632478; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_2152
Comparison: HH_023_to_029
Region: 2152

Location: lon 90.2085867, lat 22.4736576
Area: 5200 m2

NISAR observation: change=-0.3605815470218658, change_strength=0.3605815470218658, signal_percentile=0.9179487179487179, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5774268507957458; GUNW_023_HH_mean=0.5945185422897339; GUNW_029_HH_median=0.21684530377388; GUNW_029_HH_mean=0.2336122244596481; HH_023_to_029_change=-0.3605815470218658
Sentinel-1 observation: s1_median_db=-1.440387725830078, s1_min_db=-8.850478172302246, s1_max_db=8.238753318786621, s1_pct_le_minus3db=37.230769230769226; comparison-aware anomaly percentile=0.8153846153846155 (kNN stability percentile 0.7993680884676145, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3605815470218658 (band upper_quartile, percentile 0.9179487179487179); Sentinel-1 comparison-aware anomaly percentile 0.8153846153846155; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_488
Comparison: HH_023_to_029
Region: 488

Location: lon 90.1594935, lat 22.5004474
Area: 5200 m2

NISAR observation: change=-0.3373000025749206, change_strength=0.3373000025749206, signal_percentile=0.8153846153846154, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5907313823699951; GUNW_023_HH_mean=0.5823821425437927; GUNW_029_HH_median=0.2534313797950744; GUNW_029_HH_mean=0.2900440692901611; HH_023_to_029_change=-0.3373000025749206
Sentinel-1 observation: s1_median_db=0.2149260640144348, s1_min_db=-7.463374614715576, s1_max_db=10.46518898010254, s1_pct_le_minus3db=16.307692307692307; comparison-aware anomaly percentile=0.8119658119658121 (kNN stability percentile 0.8372827804107424, moderate_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=moderate_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3373000025749206 (band upper_quartile, percentile 0.8153846153846154); Sentinel-1 comparison-aware anomaly percentile 0.8119658119658121; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: moderate sensitivity to kNN neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_1041
Comparison: HH_023_to_029
Region: 1041

Location: lon 90.196999, lat 22.4916767
Area: 5600 m2

NISAR observation: change=-0.3262535333633423, change_strength=0.3262535333633423, signal_percentile=0.764102564102564, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.5405780076980591; GUNW_023_HH_mean=0.5289576649665833; GUNW_029_HH_median=0.2143244743347168; GUNW_029_HH_mean=0.2223713099956512; HH_023_to_029_change=-0.3262535333633423
Sentinel-1 observation: s1_median_db=-2.0536227226257324, s1_min_db=-11.841422080993652, s1_max_db=4.506288051605225, s1_pct_le_minus3db=38.85714285714285; comparison-aware anomaly percentile=0.8102564102564104 (kNN stability percentile 0.7535545023696683, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.3262535333633423 (band upper_quartile, percentile 0.764102564102564); Sentinel-1 comparison-aware anomaly percentile 0.8102564102564104; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_902
Comparison: HH_023_to_029
Region: 902

Location: lon 90.2059977, lat 22.494247
Area: 4000 m2

NISAR observation: change=-0.325732946395874, change_strength=0.325732946395874, signal_percentile=0.7589743589743589, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.6547638177871704; GUNW_023_HH_mean=0.624933123588562; GUNW_029_HH_median=0.3290308713912964; GUNW_029_HH_mean=0.358831912279129; HH_023_to_029_change=-0.325732946395874
Sentinel-1 observation: s1_median_db=-0.1899926215410232, s1_min_db=-6.237692356109619, s1_max_db=3.586519718170166, s1_pct_le_minus3db=22.8; comparison-aware anomaly percentile=0.7743589743589743 (kNN stability percentile 0.7488151658767772, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.325732946395874 (band upper_quartile, percentile 0.7589743589743589); Sentinel-1 comparison-aware anomaly percentile 0.7743589743589743; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: HH_023_to_029_294
Comparison: HH_023_to_029
Region: 294

Location: lon 90.1781375, lat 22.5044691
Area: 5200 m2

NISAR observation: change=-0.4015032947063446, change_strength=0.4015032947063446, signal_percentile=0.9846153846153847, signal_band=upper_quartile; coherence measurements: GUNW_023_HH_median=0.6140573024749756; GUNW_023_HH_mean=0.5939393639564514; GUNW_029_HH_median=0.2125540077686309; GUNW_029_HH_mean=0.2377904057502746; HH_023_to_029_change=-0.4015032947063446
Sentinel-1 observation: s1_median_db=0.9716353416442872, s1_min_db=-9.611207962036133, s1_max_db=9.213525772094728, s1_pct_le_minus3db=12.923076923076923; comparison-aware anomaly percentile=0.7504273504273504 (kNN stability percentile 0.740916271721959, low_sensitivity); cross_radar_status=dual_radar_upper_quartile_stable
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_023 14-day rainfall not available; gunw_029 14-day rainfall 131.93132861140086; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=195; anomaly_stability_band=low_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023.

Observation: NISAR change -0.4015032947063446 (band upper_quartile, percentile 0.9846153846153847); Sentinel-1 comparison-aware anomaly percentile 0.7504273504273504; cross-radar: both radar sources are in the upper quartile of their comparison populations, with low sensitivity to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: An unusual multi-radar signal in which both radar sources are upper-quartile for their comparison population and stable across neighbourhood sizes. This merits further investigation as a research hypothesis.
Limitation: optical verification not performed; 14-day rainfall unavailable for GUNW_023. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: VV_025_to_026_207
Comparison: VV_025_to_026
Region: 207

Location: lon 90.2196199, lat 22.5057297
Area: 4000 m2

NISAR observation: change=-0.2420695722103119, change_strength=0.2420695722103119, signal_percentile=0.25, signal_band=lower_half; coherence measurements: GUNW_025_VV_median=0.5116764307022095; GUNW_025_VV_mean=0.5120033025741577; GUNW_026_VV_median=0.2696068584918976; GUNW_026_VV_mean=0.2714565396308899; VV_025_to_026_change=-0.2420695722103119
Sentinel-1 observation: s1_median_db=-7.05075216293335, s1_min_db=-13.665271759033203, s1_max_db=2.1029090881347656, s1_pct_le_minus3db=72.39999999999999; comparison-aware anomaly percentile=1.0 (kNN stability percentile 0.9810426540284362, high_sensitivity); cross_radar_status=s1_upper_quartile_but_sensitive
Cross-radar pattern: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k)
Optical status: tested_but_inconclusive_no_valid_pixels (optical observations=2.0, valid observations=0.0, max valid pixels=0.0)
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_025 14-day rainfall 64.67995907626292; gunw_026 14-day rainfall 139.20850416637344; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=16; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023; small comparison population.

Observation: NISAR change -0.2420695722103119 (band lower_half, percentile 0.25); Sentinel-1 comparison-aware anomaly percentile 1.0; cross-radar: only the Sentinel-1 anomaly is upper-quartile, and it is sensitive to neighbourhood size (k); optical: tested_but_inconclusive_no_valid_pixels; rainfall: partial_missing_GUNW_023_14day
Inference: An upper-quartile pattern in one radar source only. The second radar source does not reinforce it, so the signal is not corroborated across radars and remains a hypothesis for further investigation.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification attempted but no valid pixels available; 14-day rainfall unavailable for GUNW_023; small comparison population. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. The comparison population for this comparison type contains only 16 candidates, so the anomaly percentile is coarse and must be treated as a limitation. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: VV_025_to_026_87
Comparison: VV_025_to_026
Region: 87

Location: lon 90.1923973, lat 22.5082479
Area: 4800 m2

NISAR observation: change=-0.2958926409482956, change_strength=0.2958926409482956, signal_percentile=0.875, signal_band=upper_quartile; coherence measurements: GUNW_025_VV_median=0.4917591214179992; GUNW_025_VV_mean=0.4970422685146332; GUNW_026_VV_median=0.1958664804697036; GUNW_026_VV_mean=0.1999053508043289; VV_025_to_026_change=-0.2958926409482956
Sentinel-1 observation: s1_median_db=-3.132713794708252, s1_min_db=-14.221352577209473, s1_max_db=4.436692714691162, s1_pct_le_minus3db=51.0; comparison-aware anomaly percentile=0.9375 (kNN stability percentile 0.8009478672985781, high_sensitivity); cross_radar_status=dual_radar_upper_quartile_but_sensitive
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_025 14-day rainfall 64.67995907626292; gunw_026 14-day rainfall 139.20850416637344; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=16; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023; small comparison population.

Observation: NISAR change -0.2958926409482956 (band upper_quartile, percentile 0.875); Sentinel-1 comparison-aware anomaly percentile 0.9375; cross-radar: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: A multi-radar signal in which both radar sources are upper-quartile for their comparison population, but the anomaly position moves with neighbourhood size. This merits further investigation with explicit attention to k-sensitivity.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023; small comparison population. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. The comparison population for this comparison type contains only 16 candidates, so the anomaly percentile is coarse and must be treated as a limitation. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

---

Candidate:
Candidate key: VV_025_to_026_415
Comparison: VV_025_to_026
Region: 415

Location: lon 90.1568177, lat 22.4999362
Area: 4800 m2

NISAR observation: change=-0.2897845208644867, change_strength=0.2897845208644867, signal_percentile=0.8125, signal_band=upper_quartile; coherence measurements: GUNW_025_VV_median=0.5858526229858398; GUNW_025_VV_mean=0.5400339365005493; GUNW_026_VV_median=0.2960681021213531; GUNW_026_VV_mean=0.2804840207099914; VV_025_to_026_change=-0.2897845208644867
Sentinel-1 observation: s1_median_db=-2.383589744567871, s1_min_db=-12.349124908447266, s1_max_db=4.714677333831787, s1_pct_le_minus3db=44.66666666666666; comparison-aware anomaly percentile=0.75 (kNN stability percentile 0.764612954186414, high_sensitivity); cross_radar_status=dual_radar_upper_quartile_but_sensitive
Cross-radar pattern: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k)
Optical status: not_tested - the absence of optical testing is not evidence that no change occurred
Environmental context: AOI-level rainfall context (not a spatial discriminator): gunw_025 14-day rainfall 64.67995907626292; gunw_026 14-day rainfall 139.20850416637344; rainfall_role=environmental_context_only
Uncertainty: comparison_population_size=16; anomaly_stability_band=high_k_sensitivity; rainfall_context_status=partial_missing_GUNW_023_14day; evidence_limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023; small comparison population.

Observation: NISAR change -0.2897845208644867 (band upper_quartile, percentile 0.8125); Sentinel-1 comparison-aware anomaly percentile 0.75; cross-radar: both radar sources are in the upper quartile of their comparison populations, but the anomaly position is sensitive to neighbourhood size (k); optical: not_tested; rainfall: partial_missing_GUNW_023_14day
Inference: A multi-radar signal in which both radar sources are upper-quartile for their comparison population, but the anomaly position moves with neighbourhood size. This merits further investigation with explicit attention to k-sensitivity.
Limitation: kNN anomaly position is sensitive to neighbourhood size; optical verification not performed; 14-day rainfall unavailable for GUNW_023; small comparison population. No independent ground-truth event label is available for erosion, deposition, bank failure or any other physical process, so the observed signal cannot be attributed to a specific process from these data alone. The comparison population for this comparison type contains only 16 candidates, so the anomaly percentile is coarse and must be treated as a limitation. Rainfall is AOI-level environmental context and is not a spatial discriminator between candidate regions.

