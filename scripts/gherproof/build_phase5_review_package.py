"""Build a provenance-aware QGIS review package from existing Phase 4B rasters.

This script deliberately does not infer a Pallimangal point or enclosure polygon.
It packages the provisional search window and actual common-valid Sentinel-1
footprint as separate, explicitly non-site layers, plus a human-review PNG.
"""
from __future__ import annotations

import json
import math
import sqlite3
import struct
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFont
from rasterio.features import shapes
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/gherproof"
OUT = DATA / "review/phase5"
MASK = DATA / "processed/sentinel1/planetary_computer/2026-01-07_2026-01-19_rtc_validity_masks_10m_utm45n.tif"
S2 = DATA / "processed/sentinel2/2026-01-13_sentinel2_visual_provisional_locality.tif"
MAP = OUT / "pallimangal_human_review_map.png"
GPKG = OUT / "pallimangal_phase5_review.gpkg"
CLARK = DATA / "reference/clark_2022_locality_context_15m_utm45n.tif"
CLARK_ZIP = DATA / "raw/Clark_Bangladesh_Aquaculture_1999_2022.zip"
MANIFEST = DATA / "manifests/phase5_site_coverage_assessment.json"


def gpkg_geometry(geom, srs_id: int) -> bytes:
    minx, miny, maxx, maxy = geom.bounds
    # GeoPackageBinary header: magic, version, little-endian + XY envelope, SRS.
    header = b"GP" + bytes((0, 1)) + struct.pack("<i", srs_id)
    header += struct.pack("<4d", minx, maxx, miny, maxy)
    return header + geom.wkb


def create_gpkg(window_geom, valid_geom, crs_wkt: str):
    if GPKG.exists():
        GPKG.unlink()
    con = sqlite3.connect(GPKG)
    cur = con.cursor()
    cur.executescript("""
    PRAGMA application_id=1196437808;
    PRAGMA user_version=10300;
    CREATE TABLE spatial_ref_sys (srs_name TEXT NOT NULL, srs_id INTEGER NOT NULL PRIMARY KEY,
      organization TEXT NOT NULL, organization_coordsys_id INTEGER NOT NULL,
      definition TEXT NOT NULL, description TEXT);
    CREATE TABLE gpkg_contents (table_name TEXT NOT NULL PRIMARY KEY, data_type TEXT NOT NULL,
      identifier TEXT UNIQUE, description TEXT DEFAULT '', last_change DATETIME NOT NULL,
      min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE, srs_id INTEGER,
      FOREIGN KEY (srs_id) REFERENCES spatial_ref_sys(srs_id));
    CREATE TABLE gpkg_geometry_columns (table_name TEXT NOT NULL, column_name TEXT NOT NULL,
      geometry_type_name TEXT NOT NULL, srs_id INTEGER NOT NULL, z TINYINT NOT NULL, m TINYINT NOT NULL,
      PRIMARY KEY (table_name,column_name), FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name),
      FOREIGN KEY (srs_id) REFERENCES spatial_ref_sys(srs_id));
    """)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    cur.execute("INSERT INTO spatial_ref_sys VALUES(?,?,?,?,?,?)", ("WGS 84 / UTM zone 45N", 32645, "EPSG", 32645, crs_wkt, ""))
    cur.execute("INSERT INTO spatial_ref_sys VALUES(?,?,?,?,?,?)", ("Undefined Cartesian", -1, "NONE", -1, "undefined", ""))
    cur.execute("INSERT INTO spatial_ref_sys VALUES(?,?,?,?,?,?)", ("Undefined Geographic", 0, "NONE", 0, "undefined", ""))
    layers = [
        ("provisional_search_window", "POLYGON", window_geom,
         ("id INTEGER", "name TEXT", "status TEXT", "source TEXT", "notes TEXT"),
         (1, "Provisional catalogue search window", "not_a_site_boundary", "Existing Phase 4B analyst bbox raster mask", "Broad locality reference only; not a village, enclosure or administrative boundary.")),
        ("common_valid_footprint", "MULTIPOLYGON", valid_geom,
         ("id INTEGER", "name TEXT", "dates TEXT", "valid_pixels INTEGER", "area_km2 REAL", "status TEXT", "source TEXT"),
         (1, "Jan 7 and Jan 19 common valid support", "2026-01-07; 2026-01-19", 463292, 46.3292, "measured_raster_footprint_not_site", "Phase 4B common validity mask; both VV/VH at both dates")),
    ]
    for layer, geomtype, geom, schema, record in layers:
        fields = ",".join(f for f in schema)
        cur.execute(f"CREATE TABLE {layer} (fid INTEGER PRIMARY KEY AUTOINCREMENT, geom BLOB NOT NULL, {fields})")
        cur.execute("INSERT INTO gpkg_contents VALUES(?,?,?,?,?,?,?,?,?,?)", (layer, "features", layer, "Phase 5 review context. Not an enclosure delineation.", now, *geom.bounds, 32645))
        cur.execute("INSERT INTO gpkg_geometry_columns VALUES(?,?,?,?,?,?)", (layer, "geom", geomtype, 32645, 0, 0))
        cur.execute(f"INSERT INTO {layer} (geom,{','.join(s.split()[0] for s in schema)}) VALUES ({','.join('?' for _ in range(len(schema)+1))})", (gpkg_geometry(geom, 32645), *record))
    con.commit()
    # Exercise SQLite integrity before delivery.
    assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    con.close()


def build_clark_context(mask_transform, mask_crs, aoi_mask, common_mask):
    """Warp the 2022 Clark categorical land-cover layer to a locality-only 15 m grid."""
    CLARK.parent.mkdir(parents=True, exist_ok=True)
    src_path = f"/vsizip/{CLARK_ZIP.as_posix()}/Bangladesh_Landcover_2022_v1exp.tif"
    resolution = 15.0
    left, top = mask_transform.c, mask_transform.f
    width = math.ceil(aoi_mask.shape[1] * abs(mask_transform.a) / resolution)
    height = math.ceil(aoi_mask.shape[0] * abs(mask_transform.e) / resolution)
    dst_transform = from_origin(left, top, resolution, resolution)
    class_grid = np.zeros((height, width), dtype="uint8")
    with rasterio.open(src_path) as src:
        reproject(src.read(1), class_grid, src_transform=src.transform, src_crs=src.crs,
                  src_nodata=src.nodata, dst_transform=dst_transform, dst_crs=mask_crs,
                  dst_nodata=0, resampling=Resampling.nearest)
    aoi_15 = np.zeros((height, width), dtype="uint8")
    common_15 = np.zeros((height, width), dtype="uint8")
    reproject(aoi_mask.astype("uint8"), aoi_15, src_transform=mask_transform, src_crs=mask_crs,
              dst_transform=dst_transform, dst_crs=mask_crs, src_nodata=0, dst_nodata=0,
              resampling=Resampling.nearest)
    reproject(common_mask.astype("uint8"), common_15, src_transform=mask_transform, src_crs=mask_crs,
              dst_transform=dst_transform, dst_crs=mask_crs, src_nodata=0, dst_nodata=0,
              resampling=Resampling.nearest)
    class_grid[(aoi_15 == 0) | (class_grid == 0)] = 0
    profile = {"driver": "GTiff", "height": height, "width": width, "count": 1,
               "dtype": "uint8", "crs": mask_crs, "transform": dst_transform,
               "nodata": 0, "compress": "DEFLATE", "tiled": True}
    with rasterio.open(CLARK, "w", **profile) as dst:
        dst.write(class_grid, 1)
        dst.set_band_description(1, "Clark Labs Bangladesh Landcover 2022 class")
        dst.update_tags(source="Clark Labs Bangladesh Land Cover and Change Maps, 2022",
                        source_archive="data/gherproof/raw/Clark_Bangladesh_Aquaculture_1999_2022.zip",
                        native_resolution_m=15, output_grid_resolution_m=15,
                        resampling="nearest-neighbour; categorical values preserved",
                        status="historical regional context only; not 2026 parcel truth or Pallimangal boundary",
                        license="Clark download page states non-commercial use; see license provenance manifest",
                        class_legend="1 Mangrove; 2 Coastal wetland; 3 Pond aquaculture; 4 Water; 5 Other landcover; 6 Missing; 0 NoData")
        dst.write_colormap(1, {0:(0,0,0,0),1:(34,139,34,255),2:(74,168,155,255),3:(35,110,190,255),4:(20,70,150,255),5:(210,190,130,255),6:(160,160,160,255)})
    legend = {"1":"Mangrove","2":"Coastal wetland","3":"Pond aquaculture","4":"Water","5":"Other landcover","6":"Missing"}
    assert set(np.unique(class_grid)).issubset({0, 1, 2, 3, 4, 5, 6})
    assert np.any((aoi_15 == 1) & (class_grid != 0))
    assert np.any((common_15 == 1) & (class_grid != 0))
    def counts(selection):
        vals, nums = np.unique(class_grid[selection], return_counts=True)
        return {legend[str(int(v))]: {"pixels_15m": int(n), "area_km2_nominal": float(n * resolution * resolution / 1e6)}
                for v,n in zip(vals,nums) if str(int(v)) in legend}
    return {"path":str(CLARK.relative_to(ROOT)).replace("\\","/"),
            "source_member":"Bangladesh_Landcover_2022_v1exp.tif",
            "source_crs":"WGS84 Normal Aspect Cylindrical Equal Area, standard parallel 15 degrees",
            "native_resolution_m":15, "output_crs":mask_crs.to_string(), "output_grid_resolution_m":15,
            "resampling":"nearest neighbour", "class_legend":legend,
            "provisional_window_class_counts":counts((aoi_15==1)&(class_grid!=0)),
            "common_s1_support_class_counts":counts((common_15==1)&(class_grid!=0)),
            "limitations":["2022 historical landcover, not temporally current in Jan 2026",
              "Class 5 is generic other landcover, not an explicit cropland reference",
              "Class 3 is country-scale pond aquaculture, not Pallimangal or parcel boundary",
              "Class 4 is not a validated permanent-water reference",
              "AOI is broad provisional locality, not target site"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with rasterio.open(MASK) as msrc:
        bands = msrc.read()
        transform, crs = msrc.transform, msrc.crs
        descriptions = msrc.descriptions
        common = bands[2] == 1
        aoi = bands[3] == 1
        assert common.sum() == 463292 and np.all(common <= aoi)
        aoi_geoms = [shape(g) for g, v in shapes(aoi.astype("uint8"), mask=aoi, transform=transform) if v == 1]
        valid_geoms = [shape(g) for g, v in shapes(common.astype("uint8"), mask=common, transform=transform) if v == 1]
        window_geom = unary_union(aoi_geoms)
        valid_geom = unary_union(valid_geoms)
        if valid_geom.geom_type == "Polygon":
            from shapely.geometry import MultiPolygon
            valid_geom = MultiPolygon([valid_geom])
        pixel_area = abs(transform.a * transform.e - transform.b * transform.d)
        assert abs(common.sum() * pixel_area / 1e6 - 46.3292) < 0.0001
    create_gpkg(window_geom, valid_geom, crs.to_wkt())
    clark_summary = build_clark_context(transform, crs, aoi, common)

    # Align Sentinel-2 RGB to the S1 mask grid for a fully reproducible static context map.
    with rasterio.open(S2) as src:
        rgb = np.zeros((3, bands.shape[1], bands.shape[2]), dtype="uint8")
        for i in range(3):
            reproject(src.read(i + 1), rgb[i], src_transform=src.transform, src_crs=src.crs,
                      dst_transform=transform, dst_crs=crs, resampling=Resampling.bilinear,
                      src_nodata=src.nodata, dst_nodata=0)
    # A subdued but legible blue overlay marks actual common validity, not inundation.
    h, w = common.shape
    rgb_img = Image.fromarray(np.moveaxis(rgb, 0, -1), "RGB")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ov = np.zeros((h, w, 4), dtype=np.uint8)
    ov[common] = (40, 154, 226, 100)
    overlay = Image.fromarray(ov, "RGBA")
    canvas = Image.alpha_composite(rgb_img.convert("RGBA"), overlay).convert("RGB")
    # Resize map body for presentation while preserving full-resolution output dimensions.
    scale = 2
    canvas = canvas.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    header_h, footer_h = 220, 150
    page = Image.new("RGB", (canvas.width, canvas.height + header_h + footer_h), "white")
    page.paste(canvas, (0, header_h))
    d = ImageDraw.Draw(page)
    font = ImageFont.load_default(size=30)
    small = ImageFont.load_default(size=22)
    d.text((38, 28), "Pallimangal site review - location not yet resolved", fill="#14212b", font=font)
    d.text((38, 72), "Reported setting: Sujatpur mouza / Beel Kedaria; village: Kultia Union, Manirampur, Jashore", fill="#263b4a", font=small)
    d.text((38, 112), "Sentinel-2B visual context: 13 Jan 2026 | blue = Jan 7/19 S1 common-valid support", fill="#263b4a", font=small)
    fy = header_h + canvas.height + 28
    d.rectangle((40, fy, 76, fy + 30), fill=(40, 154, 226), outline="#194969")
    d.text((92, fy + 2), "Common valid S1 VV/VH pixels; not water/flood", fill="#14212b", font=small)
    d.text((40, fy + 48), "No enclosure marker or candidate polygon: source reports only village/mouza context; exact site not geolocated.", fill="#8b2f26", font=small)
    d.text((40, fy + 84), "Dashed outline = broad provisional search window only; not an administrative or farm boundary.", fill="#263b4a", font=small)
    # Delineate the provisional raster window's edge for orientation; it is not a site boundary.
    left, top, right, bottom = 0, header_h, page.width - 1, header_h + canvas.height - 1
    dash, gap = 26, 18
    for x in range(left, right, dash + gap):
        d.line((x, top, min(x + dash, right), top), fill="#f7f7f7", width=5)
        d.line((x, bottom, min(x + dash, right), bottom), fill="#f7f7f7", width=5)
    for y in range(top, bottom, dash + gap):
        d.line((left, y, left, min(y + dash, bottom)), fill="#f7f7f7", width=5)
        d.line((right, y, right, min(y + dash, bottom)), fill="#f7f7f7", width=5)
    page.save(MAP, dpi=(220, 220), optimize=True)

    coverage = {
      "case_id": "GHERPROOF-SUJATPUR-2026-01",
      "created_at_utc": datetime.now(timezone.utc).isoformat(),
      "site_location_status": "reported_mouza_beel_context_identified_no_georeferenced_point",
      "boundary_status": "not_delineated",
      "enclosure_geometry": None,
      "reported_site_context": {"toponyms": ["Sujatpur mouza", "Beel Kedaria", "Bhavadah"], "confidence": "moderate for reported place-name association; low for exact coordinate or parcel", "evidence": ["Samakal 2026-01-16 reports Pallimangal fish farm in Sujatpur mouza in Beel Kedaria and south-side breach beside a khal", "Dhaka Post 2026-01-16 and Daily Country Today 2026-01-17 corroborate named gher and affected villages"], "coordinates": None},
      "coverage": {"status": "not_evaluated_for_enclosure_without_geometry", "jan_7_jan_19_common_valid_pixels_in_broad_window": int(common.sum()),
        "common_valid_area_km2": float(common.sum() * pixel_area / 1e6), "fraction_of_provisional_window": float(common.sum()/aoi.sum()),
        "provisional_window_pixel_count": int(aoi.sum()), "enclosure_total_area_m2": None, "enclosure_valid_pixels": None, "enclosure_coverage_fraction": None,
        "buffers": [], "reason": "No credible coordinate or enclosure polygon. Broad search-window coverage is not a substitute."},
      "context": {"sentinel2": "data/gherproof/processed/sentinel2/2026-01-13_sentinel2_visual_provisional_locality.tif", "s1_common_mask": str(MASK.relative_to(ROOT)).replace('\\','/'), "gpkg": str(GPKG.relative_to(ROOT)).replace('\\','/'), "map": str(MAP.relative_to(ROOT)).replace('\\','/')},
      "source_assessment": {"administrative": "DPHE Jessore geo-code table confirms Jessore/Manirampur/Kultia/Sujatpur; official Kultia Union Parishad representative page corroborates Sujatpur village address", "official_land_map_portal": "https://map.land.gov.bd/ describes digitized/georeferenced mouza/plot mapping, but no Sujatpur sheet or plot was retrieved", "lged_map": "https://oldweb.lged.gov.bd/UploadedDocument/Map/KHULNA/jessore/monirampur/monirampur.pdf provides upazila/union/roads/embankment/khal/water-body context; it disclaims authority outside LGED and has no Pallimangal geometry", "mouza_index": "https://www.zsojessore.gov.bd/maps.html is an official map index; target sheet not acquired", "third_party_index": "https://mowjabd.vercel.app/ is a third-party interface; not used as government evidence", "osm": "Existing search found no named Pallimangal feature; OSM is incomplete"},
      "land_reference_status": {"cropland": "not_delineated_at_target_site; Clark class 5 is other landcover, not a crop label", "permanent_water": "not_delineated_at_target_site; Clark class 4 is historical water, not permanence-validated", "historical_clark_2022": clark_summary, "osm": "no Pallimangal enclosure feature identified in prior documented query; OSM remains incomplete reference"},
      "readiness": "partially_ready",
      "readiness_basis": ["Administrative village-level reference is identified.", "Existing S1 scene pair and common valid raster footprint are verified over part of the provisional window.", "No exact site point/boundary; target coverage and outside agricultural coverage are unknown.", "No reviewed cropland or permanent-water reference layers."]
    }
    MANIFEST.write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gpkg": str(GPKG), "map": str(MAP), "manifest": str(MANIFEST), "valid_pixels": int(common.sum()), "aoi_pixels": int(aoi.sum()), "layers": ["provisional_search_window", "common_valid_footprint"]}, indent=2))


if __name__ == "__main__":
    main()
