# DHARA — NASA Space Apps Video 2 Factual Audit

**Audit date:** 2026-11-13
**Scope:** Read-only review of active DHARA code, project reports, manifests, raster provenance, API contracts and recorded verification. No source, data, manifests, models, frontend or historical records were changed. This report is the only file created for the audit.

## Executive findings

DHARA is an Earth Whisper feature for exploratory water-change and fisheries-incident screening. The current Pallimangal case combines real ESA/Copernicus Sentinel-1 RTC and Sentinel-2 L2A evidence, two existing Sentinel-1 water-segmentation models, historical land-cover context, and a persistent fisheries investigation API. Its strongest video story is transparent evidence triage: it organizes reported claims, prepared observations, model outputs, uncertainties, and a next field-check workflow.

There is a material challenge-alignment gap. The selected 2026 challenge, **Dancing with the SARs**, specifically calls for an interactive application using NASA-ISRO NISAR radar observations. NISAR is not used in the active DHARA Pallimangal case. Sentinel-1 and Sentinel-2 are genuine Copernicus/ESA data, not NISAR data. The separate Earth Whisper NISAR workspace and retired DELTAQ/Polder 29 work are not evidence that DHARA's Pallimangal case used NISAR. The final video must disclose this plainly and must not imply NASA imagery powered this case.

Other essential limits: the reported January 14 date is inferred from secondary reporting; the exact enclosure boundary is unresolved; the two water-change counts are optical candidate cells, not confirmed flood pixels or affected area; the ML scores are benchmark results, not Bangladesh or fisheries accuracy; and no local field labels exist. The current model readiness remains exploratory.

## 1. Project and challenge

| Item | Repository evidence | Audit finding |
|---|---|---|
| Current feature name | Frontend constants, route metadata, navigation and results screen | **DHARA** |
| Parent application | Shared shell and root branding | **Earth Whisper** |
| Team name | `README.md` uses “AquaByte”; `docs/NASA_SPACE_APPS_SUBMISSION.md` uses “Aquabyte” | Team name is recorded with inconsistent capitalization; use **AquaByte** only after checking the official team page. |
| Full team member names | No complete roster found in the reviewed active project documentation | **Not established by this repository audit.** Confirm names and spelling from the official team roster before recording credits. |
| Selected challenge | Root README and submission document | **Dancing with the SARs**, NASA Space Apps Challenge 2026. |

The challenge's stated task is to build an interactive application that uses radar remote-sensing data from the NASA-ISRO NISAR mission to track and visualize one or more kinds of surface change around the world. The official challenge page is [Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/). NASA describes NISAR as a joint NASA–ISRO mission; its mission page describes the L- and S-band radar payloads and open data access ([NASA-ISRO NISAR mission quick facts](https://nisar.jpl.nasa.gov/mission/quick-facts/)).

DHARA does meet the broad product form: an interactive map-based investigation experience that visualizes surface/water-related evidence and communicates uncertainty. It does **not** meet the challenge's central named-mission data requirement in the Pallimangal case. This is a **material challenge-alignment concern**, not a wording issue. The older Earth Whisper project has separate NISAR-related work for other investigations, but it must not be presented as input to DHARA's current fisheries case. If the team submits DHARA under this challenge, the video should state that NISAR was unavailable/not integrated for this case and that the present demonstration uses Copernicus observations. Do not claim that using Sentinel-1 substitutes for NISAR.

## 2. Problem and solution

### What is reported

The seeded case describes a **reported southern embankment failure associated with the named Pallimangal fisheries enclosure**, in Sujatpur mouza / Beel Kedaria / Bhavadah context, Manirampur, Jashore. The incident date stored as January 14, 2026 has status `reported_inferred`: sources published January 15–17 describe a Wednesday event, but no independently verified timestamp is stored. The provenance record cites Dhaka Post, Samakal and Daily Country Today as secondary sources. They do not provide a georeferenced enclosure boundary.

Media figures are not satellite measurements. Samakal reports 158 hectares of crop damage; Daily Country Today reports 1,500 bighas and more than 500 families. These are attributed, unverified claims and differ across reports. They should not be repeated as established impacts in the video. Safer wording: “Local reporting described an embankment failure; DHARA treats that as a report to investigate, not as a satellite-confirmed event.”

### Need and product role

The practical motivation is that a reported event may affect multiple nearby assets and communities, while field access, location certainty and records can be incomplete. That is a project rationale, not a measured finding that manual inspection is generally insufficient. Satellites can add regional context and help organize inspection questions; they do not replace local inspection or verify a particular enclosure without a trustworthy location and boundary.

DHARA provides an evidence-linked case page with registered satellite observations, historical land-cover context, exploratory model layers, optical change candidates, missing-information flags, review priorities, and a generated JSON investigation report. A fisheries officer or investigator can use it to review the reported case, compare the dated evidence, see what remains unknown, and prioritize a field visit to identify the site and inspect the embankment/khal. The screen explicitly frames this as exploratory screening and does not diagnose a breach or damage.

Unlike a basic satellite-image viewer, the implemented flow attaches dates, source records, processing provenance, quality/mask information, model disagreement and evidence limitations to the map. The analysis products are prepared before a user opens the case; the browser requests and displays saved evidence and does not rerun satellite processing or model inference on click.

**Separate reported facts from project assumptions:** the named incident and broad locality come from secondary reports. January 14 is an inferred date. The selection of a provisional study extent, optical thresholds, model threshold and “candidate” categories are engineering/analysis choices. They do not establish the actual enclosure, damage, cause or water extent.

## 3. NASA and space-agency data audit

The active-case inventory reviewed here includes `data/gherproof/`, its evidence registry and acquisition manifests, processing manifests, model-input/inference manifests, API service records and the frontend's registered map choices. File search found no NISAR/GCOV/GUNW/GSLC/RSLC product in the active `data/gherproof/` tree. The evidence registry reports six verified satellite observations for the case and no NISAR product record. Archived DELTAQ/Polder 29 observations are intentionally excluded. This conclusion is specific to the **DHARA fisheries case**, not every historical Earth Whisper project.

### A. NISAR

| Check | Active DHARA Pallimangal case |
|---|---|
| NISAR acquisitions / product identifiers | None found in the active case manifests or raster inventory. |
| Downloaded NISAR HDF5 or GCOV/GSLC/GUNW/RSLC | None found under `data/gherproof/`. |
| NISAR raster validation / processing | None for this case. |
| Use in this fisheries investigation | None. The map layers, training inputs and displayed case outputs are Sentinel/optical or model-derived from Sentinel-1. |
| Historical NISAR work | Separate Earth Whisper investigation/workspace material exists outside DHARA; archived DELTAQ Polder 29 material is not this case's evidence. |

NISAR suitability cannot be inferred from the project's old NISAR work or challenge entry. There is no NISAR observation in the DHARA fisheries evidence path to credit as an input.

### B. Sentinel-1

Sentinel-1 is the European Copernicus C-band SAR mission. The actual RTC data in the case were discovered and read through Microsoft's Planetary Computer STAC/COG service; the underlying mission/data are Sentinel-1A / Copernicus, and Microsoft Planetary Computer is an access/processing platform, not a satellite agency. ESA describes Sentinel-1 as a Copernicus radar mission ([ESA Sentinel-1](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1)).

**Event-focused orbit-114 pair:** January 7 and January 19, 2026, S1A IW GRD-derived RTC, ascending relative orbit 114, VV/VH. `docs/GHERPROOF_PHASE4B_REPORT.md` records successful anonymous RTC COG byte-range reads, source raster opening/sample reads, and two locally clipped, QC-checked, two-band products. The full approximately 1.8 GB source scene files were not downloaded. The separate original CDSE OData GRD VV/VH assets remain marked authentication-blocked in `event_imagery_manifest.json`; the RTC COGs are alternative RTC representations of the same acquisitions, not those CDSE GRD files. The local RTC clips are linear gamma-naught intensity, 10 m, EPSG:32645 after common-grid processing. There are **463,292** common-valid pixels (about **46.33 km²**) across the **18.13% common-valid portion of the approximately 255.58 km² provisional search window**. This is footprint coverage only; whether it includes the actual gher is unknown. The January 7/19 pair supports a cautious backscatter comparison on that common support; it does not confirm event causality, inundation, a breach, or impacts.

**Regional model-input observations:** four other S1A IW VV/VH RTC scenes were processed for Phase 7: Jan 9 and Jan 21 (relative orbit 150, descending), and Jan 12 and Jan 24 (relative orbit 12, ascending). They are kept as two separate geometry pairs. Each pair has 6,475,371 common-valid 10 m pixels over the provisional regional AOI (reported about 647.537 km²). They were used for experimental model inference and cross-sensor comparisons, not as a locally validated event-impact measurement. The inference pipeline converted positive finite linear RTC Gamma0 values to dB once, used checkpoint-specific normalization, a common VV/VH mask, and tiled inference; output probabilities/masks are exploratory model predictions.

Thus the case has **six S1 acquisition dates represented in outputs** (Jan 7, 9, 12, 19, 21, 24), but these are not six equivalent same-orbit observations or six processed GRD scenes. Jan 7/19 are local clipped RTC evidence; Jan 9/12/21/24 are separate regional RTC model inputs. The project reports explicitly state there are zero fully processed Sentinel-1 GRD scenes.

### C. Sentinel-2

Sentinel-2 is an ESA/Copernicus optical multispectral mission ([ESA Sentinel-2](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/)). DHARA uses real Sentinel-2B L2A data, accessed from Microsoft Planetary Computer COG/STAC assets. The processed reflectance/index comparison is for **January 10 and January 20, 2026** (tile 45QYF, relative orbit 133, baseline 05.11); the January 13 true-colour crop is separate regional context imagery and is not a validated classification.

The Phase 8B processing used B03 green and B08 near-infrared at 10 m, and native B11 shortwave infrared at 20 m. B03/B08 were area-averaged to the B11 20 m comparison grid with all four contributing 10 m cells valid. Surface reflectance was derived using the scene metadata formula `(DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE`, with quantification value 10,000 and −1,000 offsets for the used bands; DN zero was NoData. The SCL band was used for cloud/invalid/land-water context. NDWI used green and NIR; MNDWI used green and SWIR. For the conservative weak-reference rule, weak water requires SCL 6 and both indices ≥0; weak non-water requires SCL 4/5 and both indices <0. Conflicts and SCL 2/7 remain uncertain; invalid classes/no-data are excluded. Threshold sensitivity was also retained. These are **automated optical weak-reference categories**, not hand-labeled truth.

The Jan 13 image uses B04/B03/B02 true colour only as broad locality context. No visual parcel was assigned to Pallimangal. The Jan 10/20 optical outputs provide the temporal change candidates and optical weak-reference comparison; two optical dates cannot attribute a change to the reported Jan 14 incident.

### D. Other datasets and platforms

| Dataset / source | Role in DHARA | Status and credit/rights note |
|---|---|---|
| Sen1Floods11 v1.1 | Sentinel-1 VV/VH dB chips and hand labels for benchmark training/evaluation | Actually used for benchmark experiments. Official collection metadata are reported as proprietary / without a clear permissive dataset license; do not redistribute imagery, labels, or derived fine-tuned weights until written terms are clarified. |
| TorchGeo / SSL4EO-S12 Sentinel-1 MoCo ResNet50 weights | Self-supervised encoder initialization for the pretrained fine-tuned model | Actually used for the encoder initialization; this is not a pre-trained flood classifier. Model card records CC BY 4.0; credit TorchGeo and SSL4EO-S12 and preserve the license/attribution. |
| Clark Labs Bangladesh 2022 aquaculture map | Historical pond-aquaculture and broad land-context comparison | Context only; not a 2026 farm inventory or Pallimangal boundary. The report calculates 2.317275 km² of class 3 (pond aquaculture) within 102.23415 km² of valid mapped coverage in the provisional AOI. Clark's page says non-commercial use and permission for other uses; use attribution and do not redistribute the source archive. |
| ESA WorldCover 2021 v200 | Historical cropland, permanent-water and land-cover context | Context only; not 2026 ground truth. Manifest records CC BY 4.0 attribution. |
| Bangladesh Department of Fisheries Yearbook 2024–25 summary | Optional national-scale context in the generated report | Reports 31.07 lakh metric tonnes aquaculture production out of 51.11 lakh metric tonnes total fish production nationally. It is not a Manirampur/Pallimangal estimate. |
| Microsoft Planetary Computer | STAC discovery and access to Sentinel-1 RTC / Sentinel-2 COGs; ancillary signing and data-serving | Platform/provider role, not the space agency and not the origin of the satellite mission. The RTC collection metadata identify Catalyst processing and a CC BY 4.0 collection license; cite the underlying Copernicus data and processing/access provider accurately. |
| Copernicus Data Space Ecosystem (CDSE) | Catalogue search for event GRD assets | Catalogue-only for the four original VV/VH GRD asset URLs in `event_imagery_manifest.json`; those are authentication-blocked and must not be described as downloaded. The separate Planetary Computer RTC products were read/clipped. |
| OpenStreetMap / Leaflet | Optional basemap and interactive map software | OSM tile use requires browser network and attribution; no OSM feature was used as a Pallimangal boundary. Leaflet is the open-source web-map library. |
| NASA data (including NISAR) | No active DHARA Pallimangal measurement input identified | **Not used in this case analysis.** Do not name NASA as the provider of the plotted fisheries observations. |

The project also has older NASA/ISRO NISAR materials for separate Earth Whisper case work. Do not conflate those with the active DHARA evidence. There is no NISAR source in the DHARA case's active manifests, inputs or registered output layers examined for this audit.

### E. Challenge and partner-data declarations

The case does use Copernicus/ESA Sentinel data, which is an accurate space-agency partner data declaration. Its documentation identifies the data providers and source terms, but the video and final submission must explicitly distinguish Sentinel-1/2 from NISAR. A truthful declaration is provided in Part 9D. Do not state “NASA satellite data powered the Pallimangal analysis,” “we analyzed NISAR over Pallimangal,” or imply a NASA observation if the evidence list does not contain one.

## 4. Machine-learning audit

Both current segmentation checkpoints were trained on Sen1Floods11. Both take two channels in VV then VH order, based on Sentinel-1 GRD dB training chips. Benchmark results are from event-grouped held-out benchmark chips and are not a Bangladesh evaluation. The later training report supersedes older scratch-only score summaries.

| Model | Actual architecture / initialization | Training and input | Event-11 validation | Separate Bolivia event test |
|---|---|---|---|---|
| Scratch model | Four-scale residual Attention U-Net; 509,564 parameters; random initialization | 210 usable train chips; 13 epochs, early stopping; seed 42; 256×256 patches, batch 4; VV/VH dB; CPU-only PyTorch, no CUDA/mixed precision | IoU **0.5088**, precision **0.6469**, recall **0.7044**, F1 **0.6744**, PR-AUC/AP **0.72684** | IoU **0.6276**, precision **0.7423**, recall **0.8023**, F1 **0.7712**, PR-AUC/AP **0.74693** |
| Pretrained fine-tuned model | ResNet50SARUNet decoder; encoder initialized from TorchGeo/SSL4EO-S12 S1 MoCo checkpoint and loaded strictly; 37,244,737 parameters | Same event-grouped data/splits; 8 epochs, early stopping (best epoch 4); 256×256 patches, seed 42; later encoder stages plus decoder fine-tuned, earlier layers/stem frozen; upstream S1 dB normalization | IoU **0.5505**, precision **0.6849**, recall **0.7371**, F1 **0.7101**, PR-AUC/AP **0.74123** | IoU **0.5942**, precision **0.8905**, recall **0.6410**, F1 **0.7454**, PR-AUC/AP **0.84058** |

The split used 210 train chips, 41 event-11 validation chips, and 15 separate Bolivia event test chips; thresholds were fixed at 0.5, and Bolivia was not used for threshold/checkpoint selection. The pretrained encoder checkpoint alone is a feature representation, not a water model; the listed scores belong to the **fine-tuned encoder-decoder segmentation model**. Bolivia shows the pretrained model's precision/AP advantage with lower recall and IoU than scratch; neither single-event result establishes a local winner.

The models output per-pixel water-like class probabilities and threshold masks, plus entropy/uncertainty and model-disagreement products. These are not calibrated probabilities of flood, waterlogging, enclosure exposure or fish loss. Phase 7 applies them experimentally to four regional RTC Sentinel-1 scenes after conversion/normalization. The RTC input domain differs from Sen1Floods11 GRD training inputs, and the reports record that domain shift.

**Local validation:** none. The Phase 7C annotation sample has 450 locations with two dates each (900 blank label slots); **0/900** were human-labeled in the reviewed reports. Phase 8B optical comparison agreement is a weak-reference diagnostic—not an accuracy result. For example, overall agreement is 83.62–93.68% depending on scene/model, but weak-water positive agreement ranges 6.17–67.74%; easy non-water agreement drives much of the higher overall rate. Optical labels are produced from SCL and index rules, not independent field labels. Local water/fisheries accuracy remains unknown.

Primary local references: `docs/GHERPROOF_TRAINING_REPORT.md`, `docs/GHERPROOF_PRETRAINED_MODEL_COMPARISON.md`, `docs/GHERPROOF_PHASE7B_REPORT.md`, `docs/GHERPROOF_PHASE7C_REPORT.md`, `docs/GHERPROOF_PHASE8B_REPORT.md`, and `data/gherproof/manifests/phase7_inference_manifest.json`.

## 5. Working application demonstration

### Launch and path

Use two terminals from the repository:

```powershell
cd backend
uvicorn app.main:app --reload
```

```powershell
cd app
npm run dev
```

Open `http://localhost:5173/dhara`. The canonical feature path is `/dhara`; `/gherproof` remains a compatibility alias. The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

### Implemented interaction flow

1. DHARA landing/introduction shows the water-monitoring statement and “Open investigation”.
2. Select the January 2026 Pallimangal reported investigation.
3. Click **Analyze Now**. The browser requests prepared evidence/status/layers plus fisheries screening, summary, findings, priorities and report JSON. It does not calculate new indices, train/infer a model or fetch a new satellite scene.
4. The results view shows the exploratory scope, candidate-count cards, map, tabs (**Satellite View**, **Fisheries Context**, **AI Screening**), a registered layer selector, map evidence/legend, key evidence cards, an investigation report dialog and expandable limitations/technical details.
5. The report dialog displays the API-generated JSON report in a readable form and source links. The evidence registry report is also linked.

The frontend source offers only registered layers and registered evidence previews. Images currently represented include Jan 10/Jan 20 Sentinel-2 true colour, Clark/WorldCover historical context, and an AI comparison preview; actual availability depends on the backend and its registered-file responses. The Jan 13 broad Sentinel-2 regional context crop is used in the intro/selection card. Map tiles are from OpenStreetMap and require network access. These are not all local source scenes as full-scene archives.

Functional source-controlled interactions include navigation across intro/select/results, selection state, retry, map tabs/layer choice, layer opacity (if rendered in the map controls), evidence preview/lightbox, report dialog, technical details, and back navigation. Do not claim an unsupported direct editing/field-inspection action in the current frontend; fisheries write endpoints are API-side and disabled by default.

### Loading warning and runtime verification

The exact previous text, “Some prepared evidence could not be loaded: status,” does **not** match the current active code. `loadGherProofData` explicitly excludes the optional `status` request from its failures list. If other optional sources fail, the current UI wording is “Some optional content is unavailable: …”; missing core fisheries screening produces a DHARA evidence-service error. **This is a source-code inspection result, not a live browser confirmation.** In this audit's restricted environment, requests to `127.0.0.1:8000` and `127.0.0.1:5173` were denied at the socket layer, so the current running application could not be reached. The latest Phase 9 report records successful fresh-server GET checks on port 8001 but also an older server on port 8000 still returning HTTP 500 for screening status; that old server needed restart. The report also says screenshot/responsive visual review was not verified. Restart the backend from current source and do a live browser smoke check before recording. No current live API/UI status is claimed here.

### Recommended 60-second screen recording

| Video time | Exact action / screen to show | Narration point |
|---|---|---|
| 0–7 s | Open `/dhara`; hold on DHARA title/tagline and Earth Whisper parent breadcrumb. | “DHARA is an Earth Whisper evidence-review workflow for reported water and fisheries events.” |
| 7–14 s | Click **Open investigation**; select the Pallimangal January 2026 card. | “This is a source-reported case; the date and location still need verification.” |
| 14–20 s | Click **Analyze Now**; wait for the results response. | “The page loads reproducible evidence prepared earlier; it does not run a new satellite analysis live.” |
| 20–31 s | Show the two optical candidate cards and their Jan 10–20 / 20 m caption. | “These are possible optical change candidates, not mapped flood area.” |
| 31–42 s | Show map, switch Satellite View → Fisheries Context → AI Screening; point at legend and provisional extent note. | “The evidence streams are separate, and the map is a provisional regional search extent.” |
| 42–51 s | Open the evidence card for model comparison/disagreement. | “Two models disagree; neither has local field validation.” |
| 51–60 s | Open **View Investigation Report** and show unresolved boundary / not-assessable limitations. | “The next action is to locate the enclosure and verify conditions in the field.” |

Avoid recording the run if the evidence service fails, key map layers are blank, or stale backend status errors return. Show the actual optional-evidence warning if it appears; do not edit or conceal it during the take.

## 6. Fisheries backend (Phase 8C)

The backend has SQLite-backed **incident**, **asset**, **incident–asset link**, and **inspection** records with Pydantic response schemas. It seeds a source-linked Pallimangal incident and reported asset. Read APIs support incident/asset list and get, links as returned on incident records, a five-question screening summary, evidence-aware findings and priorities, inspection retrieval, and a structured JSON investigation report. The screening service links only registry-known evidence IDs and separates satellite evidence from reported claims and field observations.

Priorities are information-resolution/review prompts: identify the site and boundary, then collect field evidence. They are explicitly not emergency orders or drainage-failure diagnoses. Inspection records persist in SQLite; the Phase 8C verification report records a temporary-database create/read/restart/read persistence test. The report endpoint returns JSON; the frontend renders it in a dialog (not a generated PDF).

The `GHERPROOF_FISHERIES_WRITES_ENABLED` environment variable controls mutation endpoints. Writes default off and return HTTP 503 unless explicitly opted in for trusted local development. This switch is not authentication; enabling it on a public network is not safe. The backend is not ready for unrestricted public write access.

For the Pallimangal case: geometry remains null/unresolved; asset exposure is `not_assessable`, not zero; no fish escape or mortality is measured; no production or financial loss is calculated. Read-only list/screening/report APIs and the previously verified backend tests worked according to the Phase 8C verification report. Live state in this audit's sandbox is unverified, as explained in Part 5.

## 7. Real result figures suitable for a video

| Figure | Exact source / definition | Unit, date and scope | Safe interpretation |
|---|---|---|---|
| **671** possible-new-water candidates | `data/gherproof/manifests/phase8b_weak_reference_manifest.json`; Jan 10→Jan 20 optical transition category from SCL 6 plus NDWI/MNDWI weak-reference rules on the aligned output | Grid cells on the 20 m EPSG:32645 grid; two S2B L2A observations; provisional regional search extent / raster support, not a Pallimangal polygon | “671 possible-new-water candidate cells in the optical comparison.” Do not say 671 flooded pixels or convert to enclosure damage area. |
| **1,316** possible-water-loss candidates | Same manifest and pair; `possible_water_loss_candidate` transition category | Same 20 m grid and Jan 10→20 period / provisional scope | “1,316 possible-water-decrease candidate cells.” Not a measured water loss or crop impact. |
| **20 m** | Phase 8B comparison grid aligned to native B11 | Raster pixel spacing; not the positional accuracy or minimum detectable feature size | Say “20-metre analysis grid,” not “20-metre accuracy.” |
| **Model disagreement: 9.75% / 13.44%** | Evidence registry XOR `xor_fraction` for scratch vs pretrained binary masks, `disagreement_2026-01-09_2026-01-21_rel150_descending` | Pre Jan 9: 631,223 XOR pixels (9.748%); post Jan 21: 870,049 (13.436%); regional provisional AOI, common valid support | Two models give different binary outputs on these pixels. This is not the error rate or flood probability. |
| **Model disagreement: 13.41% / 16.34%** | Evidence registry XOR `xor_fraction` for `disagreement_2026-01-12_2026-01-24_rel12_ascending` | Pre Jan 12: 868,656 (13.415%); post Jan 24: 1,058,025 (16.339%); regional provisional AOI, common valid support | Same; keep ascending orbit 12 separate from descending orbit 150. |
| **46.33 km² common-valid support** | Phase 4B Planetary Computer scene validation / local paired RTC clips: 463,292 valid 10 m cells | Jan 7/19, S1A relative orbit 114 ascending; 18.13% of that report's ~255.58 km² provisional local search window | This is radar data support only, not the enclosure footprint or affected area. It is inappropriate as an impact metric. |
| **647.537 km² common valid regional pair support** | Phase 6B / Phase 7 regional geometry-specific Sentinel-1 matched pair masks (6,475,371 cells at 10 m) | Jan 9/21 orbit 150 descending and separately Jan 12/24 orbit 12 ascending; provisional regional AOI | Raster support for these pairs, not six villages' surveyed area and not event impact. Do not blend it with the Jan 7/19 smaller search window. |
| **2.317275 km² historic pond-aquaculture class** | `data/gherproof/manifests/fisheries_context_manifest.json`; Clark 2022 class 3 within the covered footprint | 102.23415 km² valid Clark coverage inside provisional AOI; 2022 map, partial AOI | Historical mapped class area only. Not current aquaculture, not Pallimangal boundary, and subject to Clark non-commercial/permission terms. |
| **31.07 lakh metric tonnes** aquaculture production | Bangladesh Department of Fisheries 2024–25 national statistics in fisheries context manifest | Bangladesh national annual total; not site-level | Optional national context only; omit from the incident impact story. |

Weak-reference comparison metrics further show agreement of 83.62–93.68% across four scenes/models; positive agreement on optical weak-water cells ranges from 6.17% to 67.74%. Their denominator is the weak binary optical reference subset (about 1.12–1.15 million 20 m cells per S2 date) and reflects a conservative automated rule, not a human validation sample. If shown, label it **weak-reference agreement** and present the class imbalance caveat; do not call it accuracy. These numbers are unnecessary in a short video and could easily mislead without this explanation.

## 8. Video credits and AI disclosure

Repository documentation records these credits/rights. Confirm that the final video actually uses each item before adding it to the end card or description:

- **Copernicus Sentinel-1 and Sentinel-2, ESA/European Union**: name the missions and dates; note that imagery was accessed through **Microsoft Planetary Computer**. Attribute ESA/Copernicus and the relevant product/service source. The January S1 COG source is the Planetary Computer `sentinel-1-rtc` collection; the January S2 is L2A. Microsoft is not the satellite-data agency.
- **Clark Labs / Clark University**: Bangladesh Land Cover and Change Maps (2022), attribution required; Clark's download page says non-commercial use and permission for other uses. Do not redistribute the archive. This layer is historical context only.
- **ESA WorldCover 2021 v200**: include the required ESA WorldCover / modified Copernicus Sentinel data attribution and CC BY 4.0. The project uses a local contextual subset.
- **Sen1Floods11 v1.1 / Cloud to Street**: acknowledge if describing the benchmark. The repository's audit reports proprietary/unclear terms. Do not publish its chips, labels or a derived checkpoint until the rights holder's terms and permission are clarified.
- **TorchGeo / SSL4EO-S12**: credit the Sentinel-1 MoCo encoder/model card and upstream SSL4EO-S12; CC BY 4.0 attribution applies to the encoder weights. It is not itself a water-segmentation model.
- **OpenStreetMap contributors**: credit visible basemap tiles and comply with ODbL attribution. Tiles are a web map base, not satellite evidence or a Pallimangal boundary.
- **Software**: React, Vite, FastAPI, Rasterio/GDAL, PyTorch, Leaflet and React-Leaflet appear in the implementation. Include software acknowledgements in a compact technical-credit slide/description as appropriate; verify exact versions and license obligations against current package/requirements files before publication.
- **AI-assisted development/video**: `docs/NASA_SPACE_APPS_SUBMISSION.md` records Autoclaw, ChatGPT Codex and Kiro as coding assistants; ChatGPT for documentation/research/prompt structuring; Google Gemini for selected 2D animated clips. It says the final video was manually selected, cut, arranged and edited by the team. Verify this account against the actual production workflow, add a concise AI-use disclosure and credit generated clips where they appear.
- **Other stock/visual assets, audio, fonts, maps, or AI tools in Video 2**: the repo cannot prove whether the final edit uses such external materials. **Team confirmation required.** Credit the actual source/provider/license, or do not use the asset.

Do not claim Figma or a particular drone, field survey, external geospatial boundary source or local respondent imagery unless the team supplies provenance for it.

## 9. Final video fact sheet

### A. Verified facts safe to say aloud

- “DHARA is a water-monitoring and decision-support feature within Earth Whisper.”
- “The case page organizes evidence around a locally reported fisheries incident in Sujatpur; the date and exact site still need confirmation.”
- “We compared Sentinel-2 observations from January 10 and 20, 2026, and produced 671 possible-new-water and 1,316 possible-water-decrease candidate cells on a 20-metre grid.”
- “These are optical candidate indicators, not confirmed flood area or impact.”
- “We also have Sentinel-1 RTC evidence in VV and VH, with geometry-specific acquisitions; model outputs are exploratory and the two models disagree.”
- “Benchmark models were trained and tested on Sen1Floods11 event-separated data; those scores are not local accuracy.”
- “The enclosure boundary is unresolved, so enclosure exposure is not assessable. The next step is field and boundary verification.”
- “The evidence page records where each output came from and what it cannot show.”

### B. Concise technical explanation for judges

“For the optical comparison, we converted Sentinel-2 stored samples to surface reflectance using scene offsets, combined green/NIR/SWIR bands to calculate NDWI and MNDWI, and used the scene-classification layer plus fixed thresholds to create conservative weak-reference classes. For radar, Sentinel-1 RTC gamma-zero intensity was converted to dB for the existing two-channel VV/VH segmentation models, with each orbit geometry kept separate. The scratch Attention U-Net and a fine-tuned ResNet50 encoder-decoder produce exploratory per-pixel water-like scores and masks. We compare them with optical indicators and each other, while reporting uncertainty. The benchmark scores come from external labeled events; no local field labels exist, so these outputs are not locally validated water or flood probabilities. The FastAPI service links the case, assets, evidence, review priorities, persistent inspections and a JSON report.”

### C. Working demo sequence

Use the 60-second sequence in Part 5. Before filming, restart the backend from current source and check the live URL, health endpoint, fisheries screening/report responses, registered previews, and the status warning in the actual browser. The current audit could not perform that live check due the sandbox socket restriction. If the backend fails, record an explicit blocker instead of substituting screenshots or a fabricated result.

### D. Exact truthful data declaration

> “For the DHARA Pallimangal case, we used ESA/Copernicus Sentinel-1 RTC radar data and Sentinel-2 L2A optical data, accessed through Microsoft Planetary Computer; **NISAR observations are not part of this case analysis**. The model benchmark used the Sen1Floods11 dataset, and the map’s historical land context includes ESA WorldCover and Clark Labs data.”

If the video is very short, retain at least the sentence through “not part of this case analysis.” Do not imply that Planetary Computer is an agency or that Sen1Floods11 is local event truth.

### E. Claims that must not be made

- “We used NISAR over Pallimangal,” “NASA detected this event,” or any claim that NASA imagery generated these current case results.
- “DHARA confirmed the January 14 flood/breach” or “the satellite proved the embankment broke.” The incident is secondary-source-reported, and Jan 14 is inferred.
- “671 flooded cells,” “1,316 hectares,” any converted affected/flooded area, or any claimed extent inside the enclosure. These are candidate cell counts and enclosure geometry is unresolved.
- A specific exposure or number of affected ponds/villages/fields; 46.33 or 647.537 km² as incident impact.
- Any fish escape, fish mortality, production loss, financial loss, or causal conclusion.
- The benchmark IoU/F1/precision/recall/AP as “DHARA accuracy,” “Bangladesh accuracy,” local validation, or fisheries accuracy.
- Optical weak-reference agreement as accuracy/ground truth, or model XOR disagreement as an error rate.
- An exact Pallimangal boundary based on the Jan 13 image or Clark's 2022 map.
- Live model computation from clicking **Analyze Now**; outputs are prepared evidence loaded from APIs.
- Public-ready authenticated officer workflows; mutation routes are default-off but the opt-in itself is not authentication.

### F. Team information still needed before scripting

1. Official full names, preferred pronunciation, team roster order, and confirmation of team-name capitalization (“AquaByte” / “Aquabyte”).
2. Confirm that **Dancing with the SARs** is the challenge chosen in the official project submission, rather than only the repository's recorded assumption.
3. Confirm the final public demo URL / account access and provide a live-browser check after restarting the current backend; the current restricted audit could not connect to localhost.
4. Confirm production credits: which AI tools were used for this particular video, which Gemini clips appear, who did editing, and all external stock images/music/fonts/visuals used.
5. Confirm whether the team has any newly available NISAR imagery intended for this exact case. If not, keep the data declaration above and explicitly describe the challenge gap.
6. Confirm approved permissions/attributions for Sen1Floods11 and Clark Labs if model weights, maps, or benchmark imagery will be publicly distributed. Current repository documentation says Sen1Floods11 redistribution rights are unresolved and Clark use is limited to non-commercial use without permission.

### G. Recommended 230-second presentation structure

Target **230 seconds (3:50)**, leaving approximately ten seconds under a four-minute ceiling. Keep the spoken word count low enough for clear narration; the times below include screen transitions.

| Time | Segment | Content |
|---|---|---|
| 0:00–0:25 (25 s) | **WHO** | Introduce team AquaByte (after confirming roster) and DHARA within Earth Whisper. Say the broad role: satellite-powered environmental monitoring and decision support. |
| 0:25–0:55 (30 s) | **WHY** | Attribute the Jan 2026 Pallimangal embankment report to local news, explain that the place/date remain unverified, and frame the need to connect reported incidents with evidence and field follow-up. |
| 0:55–1:25 (30 s) | **WHAT** | State the truthful Sentinel-1/2 data declaration and the absence of NISAR in this case. Briefly explain that Microsoft Planetary Computer served the Copernicus data. |
| 1:25–2:25 (60 s) | **DEMO** | Use the 60-second path in Part 5: DHARA landing → select case → Analyze Now → candidate cards → map views/layers → evidence card → JSON report/limitations. |
| 2:25–3:05 (40 s) | **HOW / TECH** | Explain reflectance/NDWI/MNDWI and SCL-derived weak references; separate VV/VH radar model stream; explain benchmark-trained scratch and pretrained models without claiming local accuracy. |
| 3:05–3:35 (30 s) | **SO WHAT** | Present 671/1,316 as candidate cells, model disagreement and unresolved boundary; emphasize the evidence screen's not-assessable status and limits. |
| 3:35–3:50 (15 s) | **NEXT** | Call for a verified enclosure point/polygon, local field observations/labels, and on-ground inspection; end on DHARA/Earth Whisper identity. |

**Total: 230 seconds.** Leave any additional credits/end slate within this timing or trim the demo; do not exceed 3:50 to preserve the requested safety margin.

## Audit sources reviewed

### Repository records

- `README.md`; `docs/NASA_SPACE_APPS_SUBMISSION.md`; `docs/DHARA_REBRANDING_REPORT.md`
- `docs/GHERPROOF_PHASE2_REPORT.md`; `docs/GHERPROOF_PHASE4B_REPORT.md`; `docs/GHERPROOF_PHASE6B_REPORT.md`; `docs/GHERPROOF_PHASE7_REPORT.md`; `docs/GHERPROOF_PHASE7B_REPORT.md`; `docs/GHERPROOF_PHASE7C_REPORT.md`; `docs/GHERPROOF_PHASE8_REPORT.md`; `docs/GHERPROOF_PHASE8B_REPORT.md`; `docs/GHERPROOF_PHASE8C_REPORT.md`; `docs/GHERPROOF_PHASE8C_VERIFICATION_REPORT.md`; `docs/GHERPROOF_PHASE9_REPORT.md`
- `docs/GHERPROOF_TRAINING_REPORT.md`; `docs/GHERPROOF_PRETRAINED_MODEL_COMPARISON.md`; `docs/GHERPROOF_WEAK_REFERENCE_COMPARISON.md`; `docs/GHERPROOF_DATA_PROVENANCE.md`; `docs/GHERPROOF_BOUNDARY_PROVENANCE.md`
- Active manifests: `event_imagery_manifest.json`, `planetary_computer_event_imagery.json`, `planetary_computer_scene_validation.json`, `phase6_sentinel1_regional_manifest.json`, `phase7_optical_processing.json`, `phase7_inference_manifest.json`, `phase8b_weak_reference_manifest.json`, `phase8b_weak_reference_comparison.json`, `evidence_registry.json`, `fisheries_context_manifest.json`, `license_provenance.json`, and `enclosure_boundary_provenance.json` under `data/gherproof/manifests/`.
- Current UI and API sources: `app/src/features/gherproof/GherProofPage.tsx`, `GherProofWorkspace.tsx`, `services/gherproofApi.ts`, `app/src/router.tsx`, `backend/app/api/gherproof_fisheries.py`, and `backend/app/services/gherproof_fisheries_service.py`.

### External authoritative references

- [NASA Space Apps 2026 — Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)
- [NASA-ISRO NISAR — Quick Facts](https://nisar.jpl.nasa.gov/mission/quick-facts/)
- [ESA — Sentinel-1](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1)
- [ESA — Sentinel-2](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/)
- [Copernicus Data Space — OData API](https://documentation.dataspace.copernicus.eu/APIs/OData.html)
- [Microsoft Planetary Computer — Sentinel-1 RTC](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc)
- [Microsoft Planetary Computer — Sentinel-2 L2A](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a)
- [Sen1Floods11 source repository](https://github.com/cloudtostreet/Sen1Floods11)
- [TorchGeo Sentinel-1 MoCo model](https://huggingface.co/torchgeo/resnet50_sentinel1_all_moco) and [SSL4EO-S12](https://github.com/zhu-xlab/SSL4EO-S12)
- [Clark Labs Bangladesh aquaculture data](https://www.clarku.edu/geospatial-analytics/aquaculture-data-download/)
- [ESA WorldCover 2021](https://esa-worldcover.org/en/data-access)
- [OpenStreetMap copyright and attribution](https://www.openstreetmap.org/copyright)
