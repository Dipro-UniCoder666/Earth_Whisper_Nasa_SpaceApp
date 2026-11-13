# GherProof Phase 6B — Sentinel‑2 Pixel Validation

**Provider:** Microsoft Planetary Computer `sentinel-2-l2a`
**Candidates:** 14 STAC items, representing 13 unique acquisition dates
**AOI:** provisional regional search envelope, not village or parcel geometry
**SCL validation grid:** EPSG:32645, 20 m, 1,618,843 AOI pixels (about 647.537 km²)

## Method

The 14 exact candidate IDs saved in the Phase 6 manifest were re-fetched. The actual SCL COG for each item was range-checked and read over the AOI. Clear-data support is conservatively defined as SCL codes 2 (dark area), 4 (vegetation), 5 (bare soil), and 6 (water). Codes 0, 1, 3, 7, 8, 9, 10, and 11 were excluded. This policy is only a cloud/quality-support mask: class 6 in the SCL layer is not treated as event ground truth, and the resulting clear mask is not a water map.

The SCL support counts include actual pixel values within the AOI. All candidate SCL clips and clear masks are saved with checksums. The selected pair's spectral data were also read from the actual COG assets: B03, B04 and B08 on the shared 10 m grid, B11 on its native 20 m grid. The output samples are the source integer values retained as float32 to support a common nodata value. Rasterio reports scale 1 and offset 0 for the sources, and no reflectance scaling was applied. Treat the files as L2A stored samples, not normalized reflectance. No indices, classification, or event inference were generated.

## All candidate acquisitions

Clear support below is fraction of the 20 m AOI under the stated SCL mask. Duplicate Jan 10 observations are separate orbits and were retained as distinct acquisitions.

| Date UTC | Platform | Relative orbit / pass | SCL processing baseline | AOI clear support | EO cloud cover reported by STAC |
|---|---|---:|---:|---:|---:|
| 2026-01-03 | Sentinel-2B | 033 / descending | 05.11 | 99.6242% | 0.2275% |
| 2026-01-05 | Sentinel-2C | 133 / descending | 05.11 | 0.0000% | 99.9385% |
| 2026-01-07 | Sentinel-2A | 133 / descending | 05.11 | 99.9463% | 0.0460% |
| 2026-01-08 | Sentinel-2C | 033 / descending | 05.11 | 99.9645% | 0.0025% |
| 2026-01-10 | Sentinel-2A | 033 / descending | 05.11 | 99.9968% | 0.6492% |
| 2026-01-10 | Sentinel-2B | 133 / descending | 05.11 | 99.9935% | 1.0053% |
| 2026-01-13 | Sentinel-2B | 033 / descending | 05.11 | 99.9921% | 0.0384% |
| 2026-01-15 | Sentinel-2C | 133 / descending | 05.11 | 99.9905% | 0.1829% |
| 2026-01-18 | Sentinel-2C | 033 / descending | 05.11 | 99.9926% | 0.0315% |
| 2026-01-20 | Sentinel-2B | 133 / descending | 05.11 | 99.9904% | 0.0019% |
| 2026-01-23 | Sentinel-2B | 033 / descending | 05.11 | 99.9778% | 0.0469% |
| 2026-01-25 | Sentinel-2C | 133 / descending | 05.11 | 99.9844% | 0.0510% |
| 2026-01-28 | Sentinel-2C | 033 / descending | 05.11 | 99.9954% | 0.0068% |
| 2026-01-30 | Sentinel-2B | 133 / descending | 05.11 | 0.8436% | 40.0043% |

All 14 SCL assets were pixel-readable. Jan 5 has no pixels in the selected clear classes (its AOI pixels are SCL 8/9); Jan 30 has only 0.8436% clear support (most AOI pixels are SCL 8/10). The other 12 items have at least 99.62% support. These exceptions demonstrate why catalogue items were not treated as usable scenes without raster QA.

STAC `eo:cloud_cover` is scene-level metadata and does not replace the AOI pixel mask. Here, Jan 30's 40.0% figure is consistent with poor regional clear support. The extremely low scene-level percentages for some other scenes are not enough by themselves to claim cloud-free pixels over the AOI; actual SCL support was used instead.

## Selected same-geometry comparison

Among the 24 same-tile/same-relative-orbit pre/post combinations, the selected pair is:

| Role | Date | Platform | Relative orbit | Tile | Baseline |
|---|---|---|---:|---|---|
| Pre | 2026-01-10 | Sentinel-2B | 133 descending | 45QYF | 05.11 |
| Post | 2026-01-20 | Sentinel-2B | 133 descending | 45QYF | 05.11 |

The pair has 1,618,583 common clear SCL pixels at 20 m, or 647.4332 km² and 99.9839% of the provisional AOI. It keeps platform, tile, orbit and processing baseline consistent. Selected surface assets read successfully for both dates:

| Acquisition | Bands | Grid | Valid after SCL mask | Stored value interpretation |
|---|---|---|---:|---|
| Jan 10 | B03/B04/B08 | EPSG:32645, 10 m | 6,472,354 pixels per band | Source L2A samples; scale not applied |
| Jan 10 | B11 | EPSG:32645, native 20 m | 1,618,737 pixels | Source L2A samples; scale not applied |
| Jan 20 | B03/B04/B08 | EPSG:32645, 10 m | 6,472,158 pixels per band | Source L2A samples; scale not applied |
| Jan 20 | B11 | EPSG:32645, native 20 m | 1,618,688 pixels | Source L2A samples; scale not applied |

The 10 m bands use bilinear warping to the shared grid. The 20 m SCL clear mask is nearest-neighbor upsampled for the 10 m output masks; B11 remains 20 m. This pair is useful for clear-sky optical context and corroborative inspection. It is not an independent hydrological label and should not be fused as if it had Sentinel-1 radiometry.

## Raster QC and products

All 14 SCL rasters and all 14 clear masks are under `data/gherproof/regional/processed/phase6b/sentinel2/`. Selected source-sample bands are under `l2a_stored_values_10m/` and `l2a_stored_values_20m/`. Per-item STAC metadata, class counts, clear coverage, four-by-four regional coverage summaries, asset provenance and output checksums are in [`phase6b_sentinel2_pixel_validation.json`](../data/gherproof/manifests/phase6b_sentinel2_pixel_validation.json).

The combined Rasterio QC manifest re-opened all local output GeoTIFFs. The 20 m SCL and clear-mask outputs align on a common grid; the selected 10 m bands align with each other and the shared EPSG:32645 grid. No NaN or infinite values were found. SCL output uses 255 as nodata/outside AOI; the clear mask uses 1=clear code 2/4/5/6, 0=excluded/invalid in AOI, and 255=outside AOI. The same convention is recorded in product tags.

![Per-acquisition coverage chart and spatial support cells](../data/gherproof/regional/processed/phase6b/figures/phase6b_candidate_coverage.png)

## Limitations

- The footprint is the provisional regional search extent, not authoritative boundaries for villages, an enclosure, agricultural parcels, canals, or permanent water.
- SCL clear pixels are only usable-data support. SCL classes are not field-verified water labels for the Jan 14 event.
- The raw stored values have not been converted to surface-reflectance fractions; do not compare these files numerically to normalized reflectance without applying and documenting the correct scale.
- The pair's near-complete clear support does not resolve Sentinel-1 domain shift or provide local accuracy evidence.
- No cloud-probability confidence, atmospheric uncertainty analysis, field labels, or event attribution was produced.

## Reproduction

```powershell
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/validate_candidates.py --sensor sentinel2
backend/.venv/Scripts/python.exe scripts/gherproof/phase6b/build_report_assets.py
```

The first command reads real Planetary Computer COGs and writes Phase 6B products; the second reopens local rasters, verifies checksums and regenerates QC/coverage outputs. No model inference is run.
