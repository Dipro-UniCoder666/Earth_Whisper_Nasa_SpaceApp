# GherProof Evidence Methodology — Phase 8

## Evidence classes

The evidence registry separates source observation from processing output and human interpretation. A single acquisition can therefore produce a `verified_satellite_observation` record for its raster and separate `model_prediction` and `derived_satellite_measurement` records. Registry inclusion and file integrity do not imply a flood interpretation.

| Category | Meaning | Phase 8 examples |
|---|---|---|
| `verified_satellite_observation` | An actual acquired satellite-derived raster with recorded acquisition metadata and pixel/raster QC. | Six S1 RTC acquisition dates with local validated raster products; four are the complete Phase 7 regional full-AOI scenes and Jan 7/19 are limited local clips. |
| `catalogue_metadata` | Catalogue item or metadata crosswalk that is not a processed local raster. | Four exact S1 GRD counterparts. |
| `derived_satellite_measurement` | A reproducible transformed, masked, indexed or comparison raster. | RTC dB, S2 reflectance/NDWI/MNDWI, SCL/clear masks, Phase 7B SAR/optical comparison rasters. |
| `model_prediction` | Output or checkpoint metadata from a learned model. | Two checkpoint records, 24 date/model probability-mask-uncertainty layers and eight disagreement layers. |
| `optical_reference_interpretation` | A human interpretation workflow or label record tied to optical context. | Prepared 450-point annotation package; currently under review with zero labels. |
| `news_reported_event` | Secondary-source account of an incident. | Jan 14 reported Sujatpur event, not independently verified. |
| `provisional_geographic_reference` | Non-authoritative area used for search/context. | Six-village regional search extent. |
| `human_verified_evidence` | Independent human or field verification. | Explicitly unavailable until evidence is supplied and reviewed. |

## Status values

- `verified`: file and/or observation passed the applicable raster/data checks. This does not validate a thematic class.
- `derived`: computed measurement with documented source transformation.
- `exploratory`: model output, threshold candidate or cross-sensor comparison without local reference validation.
- `provisional`: reported event context or approximate geography.
- `unavailable`: required evidence is absent.
- `under_review`: human interpretation or unresolved metadata remains.

## Sensor measurements

The four Phase 7 Sentinel‑1 scenes are Planetary Computer RTC Gamma0 VV/VH rasters. The original linear intensity data, dB conversion and model inputs remain distinct records. Existing model inference converted finite positive Gamma0 intensity once to dB, clipped to the documented input range, normalized with each checkpoint’s own statistics and respected the common valid-data mask. This processing contract is reproducible but does not remove the RTC-versus-Sen1Floods11 measurement-domain difference.

Phase 4B also has Jan 7/19 RTC clips from exact orbit‑114 ascending acquisitions. Those are limited swath products (463,292 common-valid pixels) and are not equivalent in spatial scope to the Phase 6B regional grid. The registry explicitly tags their local-clip coverage scope. Phase 6B separately records one Jan 7 VV access failure for that broader extraction; do not treat that failed read as erasing the earlier checked clip or treat the limited clip as full-region coverage.

Sentinel‑2 Jan 10/20 products use the project’s metadata-driven BOA offset and quantification conversion. NDWI/MNDWI thresholds are sensitivity indicators only. SCL is a quality/classification layer and SCL water class is not a human label. Corrected Phase 7B SAR/optical comparison rasters use the correct 20 m grid; the known Phase 7 NDWI output-grid defect remains documented, and the earlier products were not overwritten.

## Model interpretation

Scratch and pretrained model outputs are always listed separately. The 0.5 benchmark threshold was not locally tuned. Model disagreement indicates difference between models, not probability of error. No ensemble, model winner, local accuracy or local calibration is asserted. Human optical labels remain 0/900; eventual optical interpretation will still not constitute field verification.

## Geography and event context

The broad regional extent and news report are separate records. The broad polygon is not a collection of six administrative village boundaries. The exact Pallimangal enclosure/breach geometry is unresolved. News-reported area or family counts are never used as model training labels or as satellite measurements.

## Prohibited outputs

No confirmed inundation area, affected-cropland area, village-specific flood statistic, breach diagnosis/attribution, family impact, fish mortality or financial loss is calculated or exposed by the Phase 8 API. Raster pixel counts may be metadata for QA but must not be renamed as impact area.

Primary machine-readable record: `data/gherproof/manifests/evidence_registry.json`. Regenerate from the existing manifests and file state with `backend/.venv/Scripts/python.exe scripts/gherproof/phase8/build_evidence_registry.py`.
