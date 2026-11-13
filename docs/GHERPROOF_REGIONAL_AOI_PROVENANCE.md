# GherProof Phase 6 — Regional AOI Provenance

## Status

The project still has **no official boundary polygons** for the six incident-reported villages, no official regional union boundary package in the workspace, and no georeferenced Pallimangal enclosure boundary. The Phase 6 AOI is a provisional imagery-search envelope only. It must not be displayed or described as village, mouza, union, gher, cropland, or flood extent.

## Incident-reported places and administrative evidence

Dhaka Post names Sujatpur, Hatgachha and Kultia in Manirampur and Moshiahati, Bedbhita and Bolarabad in Abhaynagar in its January 2026 incident report. It reports the event in context and does not provide geodetic village boundaries or coordinates. The [official DPHE geo-code table](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf) supports Sujatpur, Hatgachha and Kultia as villages in Kultia Union, Manirampur; it is an administrative name/code table, not a spatial boundary source.

| Reported locality | Administrative/source finding | Spatial status |
|---|---|---|
| Sujatpur | DPHE geocode table lists Sujatpur under Kultia Union, Manirampur. The Phase 5 evidence also associates the reported gher with Sujatpur mouza/Beel Kedaria context. | No authoritative point or polygon in the project. |
| Hatgachha | DPHE table lists Hatgachha under Kultia Union, Manirampur. | No authoritative point or polygon in the project. |
| Kultia | Appears in the incident village list and is also the union name. | The name is ambiguous between village and union; no village polygon in the project. |
| Moshiahati / Mashiahati | Incident report assigns it to Abhaynagar. Other administrative and address sources associate similarly spelled Mashiahati with Manirampur/Kultia. | Jurisdiction and spelling require local government confirmation; no coordinate or boundary adopted. |
| Bedbhita / Bedvita | Incident report assigns it to Abhaynagar. Local reporting places Bedvita in Abhaynagar and describes access near the Teka River; spelling varies. | No authoritative village polygon or reliable geodetic point in the project. |
| Bolarabad / Balarabad | Incident and published regional studies place the locality in Abhaynagar; a 2024 study associates it with Chalisia Union. | No authoritative village polygon or reliable geodetic point in the project. |

The names “Kulti/Kultia,” “Hatgacha/Hatgachha,” “Bolarabad/Balarabad,” and “Bedbhita/Bedvita” vary among sources. They are preserved as aliases where encountered, not normalized into a claimed official gazetteer.

## Search extent geometry

The deliverable `data/gherproof/regional/six_village_regional_search_extent.geojson` and companion GeoPackage contain one polygon with these WGS84 longitude/latitude bounds:

`[89.24, 22.92, 89.54, 23.11]`

This envelope was drawn to search the reported Manirampur/Kultia and Abhaynagar/Chalishia regional contexts together, using the reported localities, the official name/code associations above, broad publicly mapped context, and secondary locality references. A Mapcarta page based on OSM/GeoNames/Wikidata places the Kultia locality at approximately 23.0011 N, 89.3132 E; a separate Mapcarta page gives an approximate Abhaynagar upazila reference point around 23.01472 N, 89.43936 E. Neither is a village boundary or surveyed point. The rectangle edges are analyst-selected search limits, positional accuracy is unquantified, and the polygon is not suitable for village-level area statistics.

The approximate projected analysis grid is EPSG:32645 at 10 m, 3,111 columns by 2,156 rows, of which 6,475,371 pixels lie inside the AOI raster mask. The envelope’s approximate surface area is 650.13 km² using a latitude-adjusted degree-area approximation; the projected pixel-mask area is 647.54 km². This is the size of the search envelope, **not** an affected area.

Two longitude-split coverage reporting sectors in `data/gherproof/manifests/phase6_regional_valid_coverage.json` are also provisional. Their shared split at 89.39 E was chosen only to summarize raster availability west/east; it is not an upazila boundary.

## Files and use

- `data/gherproof/regional/six_village_regional_search_extent.geojson` — CRS84 polygon and incident-reported locality names.
- `data/gherproof/regional/six_village_regional_search_extent.gpkg` — equivalent GeoPackage feature.
- `data/gherproof/regional/processed/sentinel1/existing_jan07_jan19_common_valid_coverage_10m_utm45n.tif` — common valid mask from existing local clips only.
- `data/gherproof/regional/phase6_existing_s1_coverage.png` — availability overview, not flood/water classification.

Do not use these polygons to attribute any detected water change to the Pallimangal enclosure. Replace them with official BBS/DLRS village/mouza polygons, or field-surveyed locality boundaries, after source, date, scale, coordinate reference system, and positional accuracy are recorded.

## References

- [Dhaka Post, January 16, 2026 incident report](https://www.dhakapost.com/country/424238).
- [DPHE official village geo-code table](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqpryl/g/V2Ministry/o/office-dphe/2024/12/8ddc502f31b5419089076326e526d691.pdf).
- [LGED Manirampur upazila context map](https://oldweb.lged.gov.bd/UploadedDocument/Map/KHULNA/jessore/monirampur/monirampur.pdf); useful context only, not an authoritative village-boundary dataset for this analysis.
- [Kabir et al. (2024), regional waterlogging study](https://www.arfjournals.com/image/catalog/Journals%20Papers/MES/2024/No%202%20%282024%29/3_Ripul%20Kabir.pdf); secondary contextual support for village/union names.
- [Mapcarta/OSM-derived Kultia locality reference](https://mapcarta.com/34917634) and [Abhaynagar upazila reference](https://mapcarta.com/14716198); approximate reference locations only.
