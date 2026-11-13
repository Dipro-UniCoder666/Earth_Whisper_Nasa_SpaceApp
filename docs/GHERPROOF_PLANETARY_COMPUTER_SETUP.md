# GherProof Planetary Computer setup and reproduction

The Sujatpur event retrieval uses Microsoft Planetary Computer's anonymous STAC API and public SAS token endpoint. No CDSE account, Microsoft account, subscription key, or project secret is used. The `planetary-computer` SDK and `pystac-client` are not installed in the existing environment; the reproducible scripts use the documented public REST interfaces with `requests` and Rasterio instead.

Official references:

- [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/api/stac/v1)
- [Planetary Computer data-access/SAS documentation](https://planetarycomputer.microsoft.com/docs/concepts/sas/)
- [Sentinel-1 RTC collection](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc)
- [Sentinel-1 GRD collection](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-grd)

## Reproduce

From the repository root in PowerShell, with the existing backend virtual environment:

```powershell
backend\.venv\Scripts\python.exe scripts/gherproof/retrieve_planetary_computer_event.py
backend\.venv\Scripts\python.exe scripts/gherproof/validate_planetary_computer_event.py
```

The retrieval script queries both exact dates separately in `sentinel-1-rtc` and `sentinel-1-grd` using the documented provisional bbox. It selects a same-acquisition RTC item only when provider properties and shared sensing/orbit/datatake ID fields match the CDSE candidate. It requests an anonymous, short-lived RTC SAS token from the official endpoint in memory, performs bounded byte-range checks, opens the COGs through GDAL/Rasterio, and reads only the provisional AOI window. It retries transient API rate-limit/server responses with bounded exponential backoff. It does not save signed URLs or the SAS token.

The pipeline writes two local VV/VH clips and a validity-mask stack under `data/gherproof/processed/sentinel1/planetary_computer/`. The clips use a shared 10 m EPSG:32645 grid, nearest-neighbour resampling, original RTC values, nodata `-32768`, and a common-valid dataset mask. It does not independently normalize dates or convert values to dB. The clips are AOI products, not downloaded original full-scene files.

The independent validator checks the local rasters, hashes, grids, internal masks and valid-pixel alignment, then records its results in `data/gherproof/manifests/planetary_computer_scene_validation.json` and writes `coverage_validity.png`. A coverage mask value means data availability only; it is not a water label.

## Provenance and use limits

The RTC collection metadata declares CC BY 4.0 and identifies Catalyst as processor and Microsoft Planetary Computer as host/licensor. Attribute outputs to Microsoft Planetary Computer, Catalyst, and ESA/Copernicus Sentinel-1. Review the collection's [current licence and metadata](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-1-rtc) before redistribution. The corresponding GRD collection advertises a different `proprietary` collection licence and is not used for these outputs.

Only the broad provisional Sujatpur locality box is available; it is not the Pallimangal enclosure boundary. Common valid SAR coverage is partial. Do not interpret nodata as non-water, infer a breach, run event inference, or calculate affected area from these products. The source COGs are not saved locally; the unsigned STAC metadata, asset references, retrieval provenance, and checksums of the local clipped products are recorded in the alternative-provider manifest.
