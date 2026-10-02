# Earth Whisper - Scientific Data & Methodology

This document describes the scientific workflow, NASA/Earth-observation data
usage, processing pipeline, provenance, and technical methodology of the Earth
Whisper repository. It is written from the repository's own verified artifacts,
scripts, and documentation. It intentionally describes the **overall Earth
Whisper flow** rather than attributing every dataset to one geographic
location, and it does not claim any physical cause that the repository does not
establish.

**Status legend used throughout:**

| Label | Meaning |
|---|---|
| Implemented | Present and executed by repository code/artifacts |
| Partially implemented | Present for part of the pipeline or with documented gaps |
| Static / precomputed | Verified artifact produced offline and served as-is |
| Inference-only | Statistical prioritization, not physical attribution |
| Attempted / inconclusive | Executed but produced no usable result |
| Committed but unused | Present in the repository, not referenced by processing code |
| Live metadata-only | Runtime call that retrieves metadata, never science rasters |
| Planned / not implemented | Documented intent with no implementation |

---

## 1. Scientific Objective

Earth Whisper is an interactive Earth-observation investigation experience
built around NASA-ISRO NISAR radar observations. Its scientific objective is to:

- Identify **where** Earth-observation signals change, using NISAR
  interferometric coherence as the primary observation.
- Investigate those changes with **multiple, independent observations** rather
  than a single sensor.
- Organize **evidence, uncertainty, and provenance** so that each finding can be
  traced back to the dataset, method, and limitation that produced it.
- **Avoid forcing a causal explanation from one signal.** A radar-signal change
  is not, by itself, a confirmed physical event or a confirmed cause.

These goals are governed by `docs/science/scientific-principles.md`, whose
principles are treated as non-negotiable design constraints. In particular:
NISAR detects and characterizes change but does not explain cause; additional
evidence helps investigate but does not "confirm"; uncertainty is a first-class
output; and "undetermined" / "insufficient evidence" are valid, expected
answers.

## 2. End-to-End Scientific Workflow

The pipeline below reflects the repository's actual processing steps and uses
the terminology already present in it (candidate, comparison, coherence
change, cross-check, feature engine, anomaly prioritization, uncertainty,
investigator subset, Event Case File).

```
Earth observation
  -> NISAR radar observations (GUNW coherence products)
  -> AOI extraction on the common GUNW grid
  -> temporal comparison (same-polarization acquisition pairs)
  -> coherence change (delta coherence = later - earlier)
  -> spatially connected candidate regions (8-connectivity)
  -> region-level temporal fingerprint (all available GUNW observations)
  -> independent radar cross-check (Sentinel-1 backscatter change)
  -> optical verification attempt (HLS / Sentinel-2)
  -> environmental context (GPM IMERG rainfall)
  -> feature engine (schema-driven feature table)
  -> anomaly analysis / prioritization (comparison-aware kNN)
  -> evidence fusion and uncertainty assessment
  -> investigator subset (Step 10)
  -> structured Event Case File (Step 11)
  -> runtime delivery of verified artifacts (frontend / read-only API)
```

The repository records the methodological stages as:
`NISAR coverage` -> `NISAR AOI extraction and change` -> `Temporal fingerprint`
-> `Optical verification` -> `Environmental context` -> `Feature engine` ->
`ML anomaly detection` -> `Evidence fusion` (see
`data/step11_event_case_file/earth_event_case_file.json`, `methodology_steps`).

The corresponding artifact directories are:
`data/step3_temporal_fingerprint/`, `data/step4_optical_verification/`,
`data/step5_environmental_context/`, `data/step6_feature_engine/`,
`data/step9_uncertainty_limitations/`, `data/step10_ai_investigator/`,
`data/step11_event_case_file/`, and `data/step12_backend/`.

## 3. NASA / Earth Observation Datasets Used

| Dataset | Provider | Product / Version | Role in Earth Whisper | Processing / Integration | Status |
|---|---|---|---|---|---|
| NISAR GUNW | NASA-ISRO SAR mission; accessed from NASA/ASF Earthdata Cloud | GUNW products `GUNW_023_091`, `GUNW_025_091`, `GUNW_026_091`, `GUNW_029_091`; Track 91 / Frame 77, descending | **Primary observation** - interferometric coherence and coherence change | AOI extraction on the common GUNW grid; same-polarization comparison; delta-coherence threshold; connected regions; region statistics; temporal fingerprint | Implemented (offline) |
| Sentinel-1 SAR backscatter | Copernicus Sentinel-1 (GRD); accessed via ASF/Earthdata tooling | S1D GRD scenes used for the documented 3 Jul 2026 and 15 Jul 2026 comparison | **Independent radar cross-check** for candidate regions in the broader pipeline | sigma0 VV calibration via the sigmaNought calibration LUT; dB-change layer; candidate-pixel-centered neighborhood sampling; standardized features used for anomaly prioritization | Implemented (offline) |
| NASADEM | NASA | NASADEM 1-arcsecond HGT tiles (`n30e077`, `n30e078`, `n31e077`, `n31e078` present; `n31e077.hgt` used by the terrain script) | **Terrain / elevation / slope context** | Elevation and local slope computed directly from HGT by `earth_whisper_candidate1_terrain.py`; terrain values carried into the investigation evidence | Implemented |
| GPM IMERG | NASA GPM / GES DISC (Giovanni time series export) | IMERG Late Run V07 (`GPM_3IMERGDL`) | **Rainfall / environmental context** in the broader pipeline; AOI-level, not a spatial discriminator | 3 / 7 / 14-day rainfall windows, maximum daily rainfall, wet-day counts (`data/step5_environmental_context/`); a daily time series CSV is committed at the repository root with its Giovanni reproduction URL | Implemented (context only) |
| HLS / Sentinel-2 optical | NASA HLS project | HLS S30 v2.0, tile `T46QBK`, comparison dates 26 Jun 2026 and 14 Sep 2026 | **Optical verification attempt** for a subset of candidates | `earthaccess` + `rasterio` screening of 6 candidates; result recorded as `TESTED - INCONCLUSIVE` with 0 valid pixels due to high-aerosol conditions; the remaining 205 candidates were not optically tested | Attempted / inconclusive |
| MODIS MCD12Q1 | NASA (LP DAAC product family) | Land-cover HDF file `MCD12Q1.A2024001.h24v05.061.2025206032258.hdf` committed at the repository root | None in final processing | No reference to MCD12Q1 exists in repository code or processing artifacts | Committed but unused |

Notes:

- The browser map uses Leaflet with OpenStreetMap tiles, and location search
  uses OpenStreetMap Nominatim when that workflow is used. These are **map
  services, not NASA evidence integrations**.
- **Sentinel-1 role.** Sentinel-1 was used as an **independent SAR cross-check in
  the broader Earth Whisper evidence pipeline** - comparing radar backscatter
  behavior around NISAR-identified candidate regions to strengthen the
  supporting evidence. It is an ESA/Copernicus mission, not a NASA dataset.
  It provides an independent radar observation and is not ground truth: it was
  not the primary detector, was not applied to every individual investigation
  or site, and does not by itself confirm any physical event. NISAR remains the
  primary radar observation and Sentinel-1 remains the independent cross-check
  in the broader pipeline.
- Rainfall is contextual evidence and does not prove that rainfall caused an
  observed change.

## 4. NISAR Processing Method

The NISAR workflow below is the method documented and executed by the
repository (primarily `step2_nisar_change/docs/STEP3_TEMPORAL_FINGERPRINT.md`
and its scripts, carried forward by the Step 6-11 artifacts).

1. **GUNW products.** Four interferometric GUNW products were used:
   `GUNW_023_091` (20 Jun 2026 - 02 Jul 2026, HH), `GUNW_025_091`
   (14 Jul 2026 - 31 Aug 2026, VV), `GUNW_026_091` (26 Jul 2026 - 19 Aug 2026,
   VV) and `GUNW_029_091` (31 Aug 2026 - 12 Sep 2026, HH). All use
   Track 91 / Frame 77 descending geometry. Products were accessed from
   NASA/ASF Earthdata Cloud.
2. **Coherence extraction.** Coherence layers were extracted on the common
   GUNW grid (20 m pixel spacing). A rectangular extraction of 83,356 pixels
   was reduced to 79,874 pixels by a polygon mask of the AOI (95.82%
   retention).
3. **Temporal comparison.** Two same-polarization comparisons were formed:
   HH (`GUNW_023` -> `GUNW_029`) and VV (`GUNW_025` -> `GUNW_026`).
   Polarizations are never mixed inside a comparison.
4. **Coherence-change calculation.** Change was calculated as
   `delta coherence = later coherence - earlier coherence`.
5. **Threshold / anomaly mask.** Candidate pixels were selected with
   `delta coherence <= -0.20`.
6. **Filtering / cleaning and connected regions.** Connected components were
   identified using **8-connectivity** with a **minimum region size of
   10 pixels**; each pixel represents 20 m x 20 m = 400 m2. This produced
   **211 candidate regions** inside the exact AOI.
7. **Polygonization / candidate extraction.** Candidate regions were carried
   into region-level tables (for example
   `step2_nisar_change/step2_candidate_regions_geographic.csv`) and given a
   stable identity: `candidate_key = comparison + "_" + region_id`. Because a
   region can appear in more than one comparison, `region_id` alone is never
   used as a unique identifier.
8. **Candidate statistics.** Per-candidate geometry and source change
   statistics (area, valid pixel counts, coherence statistics) are computed
   over the candidate polygon; zonal statistics are recorded as
   "mean, median, valid pixel count" in the documented methodology.
9. **Temporal fingerprinting.** For every candidate region, coherence
   statistics were extracted from all four GUNW observations, producing a
   region-level temporal fingerprint table
   (`step2_region_temporal_fingerprint.csv`).
10. **Evidence / uncertainty processing.** Downstream steps (feature engine,
    optical verification attempt, environmental context, uncertainty
    annotation, investigator subset, Event Case File) consume these candidates
    without recomputing the underlying measurements.

The QGIS/NISAR workspace in `AquaByte_NISAR/` preserves the team's raster
outputs used in this workflow (coherence and coherence-change rasters,
binary/clean change masks, anomaly masks, cluster layers, unwrapped phase).
Those artifacts are **precomputed**; the application does not recalculate them.

## 5. Statistical / Anomaly Analysis

The anomaly approach in this repository is **deterministic and statistical**,
with an **unsupervised k-nearest-neighbour (kNN) prioritization** step. It is
**not** a trained classifier, an event-classification model, or a probability
engine.

- **Feature basis.** Four standardized Sentinel-1 backscatter features are
  used for the kNN analysis: `s1_median_db`, `s1_min_db`, `s1_max_db`,
  `s1_pct_le_minus3db`. The feature engine schema
  (`data/step6_feature_engine/feature_schema.csv`) documents each feature's
  category, source, unit, description and `evidence_role` (for example
  `measured`, `context`, `quality`, `metadata`).
- **Comparison-aware populations.** Anomaly percentiles are calculated **only
  against the same comparison population** - HH (`HH_023_to_029`, 195
  candidates) and VV (`VV_025_to_026`, 16 candidates) are analyzed
  independently and are never pooled. The VV population is small, which makes
  its percentiles coarse; this is recorded as a limitation.
- **k values and stability.** The comparison-aware kNN analysis uses
  `k = 3, 5, 8` (`scripts/ml/step8b_comparison_aware_knn.py`); an earlier
  baseline uses `k = 5, 10, 20` (`scripts/ml/step7d_knn_anomaly.py`).
  Stability across k values is assessed and recorded as a stability band and as
  k-sensitivity in the cross-radar status.
- **What the percentile means.** The anomaly percentile expresses
  **statistical isolation within its comparison population**. It is not a
  probability of a physical event.
- **Cross-radar status.** A recorded status (for example
  `dual_radar_upper_quartile_stable`,
  `dual_radar_upper_quartile_but_sensitive`,
  `s1_upper_quartile_nisar_not_upper_quartile`,
  `neither_radar_measurement_upper_quartile`) summarizes how NISAR and
  Sentinel-1 measurements compare within their populations. No combined score
  or probability is created.
- **Investigator subset (Step 10).** From the 211 candidates, 32 were selected
  for the investigation subset by a documented, reproducible rule: the top 20
  by comparison-aware anomaly percentile, unioned with all candidates whose
  cross-radar status is a dual-radar upper-quartile pattern, de-duplicated by
  `candidate_key` (29 HH, 3 VV). The selection is prioritization, not
  attribution.

## 6. GIS / Processing Tools

| Tool | Role in the workflow | Evidence in repository |
|---|---|---|
| QGIS | Desktop GIS workspace used to produce and inspect the NISAR coherence and change rasters, masks, and cluster layers | `AquaByte_NISAR/` workspace and its documented "QGIS/NISAR scientific workspace" role |
| GDAL (Python `osgeo.gdal`) | Raster open/read/write and reprojection for the Sentinel-1 calibration, change layers, and NISAR/Sentinel-1 overlap and cross-check scripts | `step2_nisar_change/calibrate_s1.py`, `make_s1_change.py`, `crosscheck_nisar_s1.py`, `exact_nisar_s1_overlap.py` |
| Python (numpy / pandas) | Raster statistics, region statistics, temporal fingerprints, feature tables, kNN anomaly analysis, artifact generation | `step2_nisar_change/temporal_fingerprint.py`, `region_temporal_fingerprint.py`, `convert_regions.py`, `scripts/ml/*`, `scripts/build_step12d_casefile.py` |
| Raster calculation | Coherence-change layers (`later - earlier`) and Sentinel-1 dB-change layers | `step2_nisar_change/HH_023_to_029_coherence_change.npy`, `VV_025_to_026_coherence_change.npy` and their scripts |
| Polygonization / connected components | Spatial grouping of candidate pixels into connected regions (8-connectivity, minimum 10 pixels) | Documented in `step2_nisar_change/docs/STEP3_TEMPORAL_FINGERPRINT.md`; region tables in `step2_nisar_change/` |
| Zonal statistics | Per-candidate statistics over the candidate polygon (mean, median, valid pixel count) | Recorded in the documented methodology and in the generated feature/evidence tables (`data/step6_feature_engine/step8c_evidence_matrix.csv`) |
| Terrain calculation | Elevation and local slope from NASADEM 1-arcsecond HGT | `earth_whisper_candidate1_terrain.py` (`n31e077.hgt`) |
| earthaccess / rasterio / pyproj | Optical verification attempt against HLS data, with coordinate handling | `step2_nisar_change/step4_optical_screen.py` |

## 7. Evidence, Uncertainty & Scientific Boundaries

Earth Whisper keeps observation, interpretation, and uncertainty separate.

- **Observation is not cause.** NISAR coherence change indicates a change in
  radar-scattering consistency between observations. It does not, by itself,
  identify a physical process.
- **Anomaly is not a confirmed event.** A statistical anomaly indicates that a
  candidate is unusual within its comparison population; it is not a confirmed
  Earth-surface event.
- **Context does not prove causation.** Rainfall, terrain, and optical evidence
  narrow the space of plausible explanations; they rarely prove a single cause
  from remote data alone.
- **Inconclusive evidence stays inconclusive.** The optical attempt is recorded
  as `TESTED - INCONCLUSIVE` with 0 valid pixels; the 205 candidates that were
  not optically tested remain labeled `not_tested`. "Not tested" is never
  treated as evidence of absence.
- **Uncertainty is retained.** Comparison population size, anomaly stability
  band, k-sensitivity, rainfall context availability, and the recorded evidence
  limitation travel with each candidate.
- **Documented NISAR limitations.** The repository records, among others, that
  the four GUNW observations do not form one continuous coherence time series;
  that the comparisons mix HH and VV pairs; that interferograms have different
  temporal baselines; that a coherence decrease does not uniquely identify a
  physical process; and that candidates represent areas requiring independent
  verification rather than confirmed events.
- **The Event Case File preserves boundaries.** Evidence, provenance, and
  limitations are packaged together so that no result is presented without its
  context.
- **Valid answers include "undetermined".** The system must be able to say it
  does not know; an honest "insufficient evidence" result is preferred over a
  confident-sounding wrong one.

## 8. Runtime Architecture vs Scientific Processing

Earth Whisper strictly separates offline science from runtime delivery.

**Offline / precomputed scientific processing.** All scientific computation
(raster processing, candidate extraction, cross-checks, feature engineering,
kNN anomaly analysis, uncertainty annotation, investigator subset, case-file
generation) is performed offline and stored as artifacts under `data/`. The
repository also preserves the original scientific workspace in
`AquaByte_NISAR/`.

**Runtime delivery of verified artifacts.** The frontend reads the generated
Step 12 candidate contract. Delivery is **API-first with a static fallback**:
`app/src/features/candidates/services/candidateService.ts` requests the
configured read-only API when available and otherwise loads the bundled static
contract at `app/public/data/earth_whisper_candidates.json`. The application
cannot run without one of these two sources.

**Read-only backend.** `backend/` is a read-only FastAPI service that serves the
generated candidate contract and the Step 11 case-file artifacts
(`/api/health`, `/api/candidates`, `/api/candidates/{candidate_key}`,
`/api/candidates/{candidate_key}/evidence`, `/api/case-file`,
`/api/case-file/pdf`, and a request-time investigation assembly endpoint
`POST /api/investigations`). It does not recalculate scientific values.

**Live NASA metadata discovery (metadata-only).** The backend's
`live_eo_service.py` performs a bounded, metadata-only discovery of NISAR GUNW
collection and granule metadata through **NASA Earthdata CMR**. It
deliberately does **not** download or process raster data. Results are cached
and carry an explicit provenance status: `LIVE`, `CACHED_LIVE`, or
`VERIFIED_STATIC` when live metadata is disabled, unavailable, or fails. The
investigation assembly marks `scientific_result_status` as `VERIFIED_STATIC` in
every case: live discovery can confirm that matching NISAR products exist, but
the scientific result always comes from the verified contract.

**What is NOT recalculated at runtime.** The browser and the API do not
download raw NISAR/Sentinel-1/HLS/GPM rasters, do not recompute coherence,
coherence change, terrain, rainfall statistics, kNN percentiles, or any
scientific value, and do not derive new probabilities or causal labels.

## 9. Event Case File

The Event Case File is the structured record of an investigated candidate. It
preserves evidence, provenance, and limitations together. Depending on the
flow, it is delivered in one of three forms:

1. **Browser-generated case file** for the Monda investigation - a ZIP
   containing a summary PDF, structured JSON, data sources, methodology, and a
   readme, generated client-side by
   `app/src/features/investigation/caseFile/buildCaseFile.ts` (with
   dependency-free PDF and ZIP writers).
2. **Generated Step 11 case-file package** in
   `data/step11_event_case_file/` - `earth_event_case_file.json`,
   `earth_event_case_file.pdf`, `sources.txt`, `methodology.txt`, and a figure
   manifest, covering the investigated subset.
3. **Served case file** from the read-only backend (`/api/case-file` for the
   structured JSON and metadata, `/api/case-file/pdf` for the PDF produced by
   Step 11; the PDF is served as produced and never regenerated).

Contents include: location and coordinates; observation period; the NISAR
observations used; measured coherence-change statistics; cross-radar
(Sentinel-1) evidence; optical status; rainfall context; evidence coverage;
uncertainty (comparison population size, anomaly stability band, evidence
limitations); provenance and data sources; global limitations; and the
investigation's observation / inference / limitation statements. Missing
values are preserved as unavailable rather than replaced with zero, and the
case file never labels a physical event as confirmed.

## 10. Data Provenance & References

The following official sources are documented in the repository
(`data/step11_event_case_file/sources.txt` and the Step 11 case-file JSON):

| Source | Reference |
|---|---|
| NISAR Data User Guide | https://nisar-docs.asf.alaska.edu/ |
| NISAR GUNW product documentation | https://nisar-docs.asf.alaska.edu/gunw/ |
| NISAR Vertex search | https://nisar-docs.asf.alaska.edu/vertex/ |
| ASF Vertex | https://vertex-plus.asf.alaska.edu/ |
| NISAR product overview | https://nisar-docs.asf.alaska.edu/products-overview/ |
| HLS (Harmonized Landsat Sentinel-2) | https://www.earthdata.nasa.gov/data/projects/hls |
| NASA GPM / IMERG | https://gpm.nasa.gov/data/imerg |
| NASA Earthdata | https://www.earthdata.nasa.gov/ |
| GPM IMERG time series (Giovanni reproduction link recorded in the committed CSV header) | https://giovanni.gsfc.nasa.gov/giovanni/ |
| NASADEM distribution (OpenTopography) | https://portal.opentopography.org/ |
| Map tiles / attribution | https://www.openstreetmap.org/copyright |

Tools used for processing: **QGIS** (desktop GIS workspace) and **GDAL**
(Python `osgeo.gdal` raster I/O) - the repository documents their role but does
not record external documentation URLs for them. Additional Python libraries
used by the optical attempt are `earthaccess`, `rasterio`, and `pyproj`.

Reference note: this document intentionally avoids inventing publication
details. Where the repository does not record a citation, none is claimed here.

## 11. Reproducibility

**Reproducible from repository scripts and artifacts:**

- The Step 12 candidate data contract:
  `scripts/step12_build_data_contract.py` (deterministic join by
  `candidate_key`; values are passed through, not recomputed).
- Backend/contract validation: `scripts/step12_validate_backend.py`
  (standard-library checks of counts, identity rules, and preserved values).
- The Step 11 case-file package:
  `scripts/build_step12d_casefile.py` (reads the verified Step 3-10 tables).
- The kNN anomaly tables: `scripts/ml/step7d_knn_anomaly.py` and
  `scripts/ml/step8b_comparison_aware_knn.py` (numpy/pandas; consume the
  standardized feature table in `data/step6_feature_engine/`).
- Terrain for the documented prototype site:
  `earth_whisper_candidate1_terrain.py` (reads the committed NASADEM HGT tile).
- Frontend build and type-checking: `npm run build` / `npm run lint` in `app/`.
- Backend unit tests for the live-metadata service:
  `backend/tests/test_live_investigation.py` (offline; uses a fake CMR opener).

**Depends on external NASA access or precomputed artifacts:**

- Re-downloading NISAR GUNW products and Sentinel-1 GRD scenes from NASA/ASF
  Earthdata (the committed `.npy` layers and region tables are derived
  artifacts; the raster-processing scripts expect those inputs).
- The GPM IMERG retrieval used the committed downloader script and an
  authenticated Earthdata session (`download_files_GPM_3IMERGDL_07.py`).
- The HLS optical attempt used `earthaccess` with an authenticated session
  (`step2_nisar_change/step4_optical_screen.py`).
- The runtime application depends on the **precomputed** contract and case-file
  artifacts; the static fallback means the frontend can run without a local
  backend process.
- The read-only backend requires `fastapi` and `uvicorn`
  (`backend/requirements.txt`) to run.

## 12. Scientific Summary

**What Earth Whisper does:**

- Detects and characterizes observed surface change using NISAR interferometric
  coherence, expressed as comparison-specific coherence change.
- Identifies spatially connected candidate regions and characterizes them
  temporally across the available NISAR observations.
- Cross-checks candidates with an independent radar observation (Sentinel-1
  backscatter change) and prioritizes them statistically, within their
  comparison population, using an unsupervised kNN analysis.
- Adds terrain context (NASADEM) and environmental context (GPM IMERG
  rainfall), and records optical verification as attempted and inconclusive
  where that is what occurred.
- Organizes evidence, uncertainty, and provenance into a structured Event Case
  File, and delivers verified artifacts to the application at runtime.

**What Earth Whisper does NOT claim:**

- It does not prove a physical cause (landslide, erosion, flood, deposition, or
  any other) from a coherence anomaly or from any single signal.
- It does not classify events, and it does not produce calibrated
  probabilities - statistical percentiles express isolation within a
  comparison population, not likelihood of an event.
- It does not treat Sentinel-1 as ground truth, or rainfall as proof of
  causation.
- It does not treat "not optically tested" as evidence that nothing changed.
- It does not download or process raw satellite rasters at runtime, and it does
  not perform live NASA raster processing - live Earthdata CMR usage is
  metadata discovery only.
- It does not use a trained AI model or a language model in the current
  implementation.

Earth Whisper's contribution is an evidence organization and uncertainty
discipline: it shows where change was observed, what independent and
contextual evidence says about it, what remains unknown, and where further
investigation should focus.
