"""Add Phase 5B cadastral search status to the existing QGIS review package.

This intentionally creates no site coordinates or geometry. It adds a plain
attribute table to the existing GeoPackage and an annotated copy of the Phase 5
context map. The source map and geometry layers are left unchanged.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "data/gherproof/review/phase5"
SOURCE_MAP = REVIEW / "pallimangal_human_review_map.png"
OUTPUT_MAP = REVIEW / "pallimangal_phase5b_review_map.png"
GPKG = REVIEW / "pallimangal_phase5_review.gpkg"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def annotate_map() -> tuple[int, int]:
    if not SOURCE_MAP.is_file():
        raise FileNotFoundError(f"Existing Phase 5 map missing: {SOURCE_MAP}")
    with Image.open(SOURCE_MAP) as src:
        source = src.convert("RGB")
    width, height = source.size
    pad = max(18, width // 90)
    box_height = max(230, height // 10)
    image = Image.new("RGB", (width, height + box_height + pad * 2), (255, 255, 255))
    image.paste(source, (0, 0))
    draw = ImageDraw.Draw(image)
    top = height + pad
    draw.rounded_rectangle(
        (pad, top, width - pad, top + box_height),
        radius=max(12, width // 180),
        fill=(17, 31, 49),
        outline=(245, 188, 66),
        width=max(3, width // 1000),
    )
    title_font = font(max(28, width // 62))
    body_font = font(max(20, width // 92))
    x, y = pad * 2, top + pad
    draw.text((x, y), "PHASE 5B CADASTRAL SEARCH — NO SITE POSITION ASSERTED", font=title_font, fill=(255, 255, 255))
    y += int(title_font.size * 1.55)
    lines = [
        "Sujatapur / Sujatpur J.L. 143 is a secondary-source lead; official sheet confirmation is pending.",
        "No cadastral sheet recovered. No mouza, beel, enclosure, khal, embankment or breach geometry shown.",
        "Blue remains Jan 7/19 common-valid radar support over the broad search window, not water or flood extent.",
    ]
    for line in lines:
        draw.text((x, y), line, font=body_font, fill=(235, 241, 248))
        y += int(body_font.size * 1.35)
    image.save(OUTPUT_MAP, format="PNG", optimize=True)
    return image.size


def add_status_table() -> tuple[list[str], str]:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with sqlite3.connect(GPKG) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"GeoPackage integrity check failed before update: {integrity}")
        existing = {row[0] for row in db.execute("SELECT table_name FROM gpkg_contents")}
        required = {"provisional_search_window", "common_valid_footprint"}
        if not required.issubset(existing):
            raise RuntimeError(f"Required existing layers missing: {required - existing}")
        if "phase5b_cadastral_status" not in existing:
            db.execute(
                """CREATE TABLE phase5b_cadastral_status (
                    fid INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    mouza_name TEXT NOT NULL,
                    candidate_jl INTEGER,
                    jl_status TEXT NOT NULL,
                    official_sheet_recovered INTEGER NOT NULL,
                    boundary_status TEXT NOT NULL,
                    target_coverage_status TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    interpretation TEXT NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO phase5b_cadastral_status (
                    case_id, mouza_name, candidate_jl, jl_status,
                    official_sheet_recovered, boundary_status,
                    target_coverage_status, source_url, interpretation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "GHERPROOF-SUJATPUR-2026-01",
                    "Sujatapur / Sujatpur, Kultia, Manirampur, Jashore",
                    143,
                    "provisionally corroborated from a secondary listing; not officially verified",
                    0,
                    "not_delineated",
                    "not evaluated; no supported site geometry",
                    "https://dolilsheba.com/mouza/land-office/152",
                    "No map coordinates or boundary inferred. Confirm JL from official cadastral sheet or DLRS index.",
                ),
            )
            db.execute(
                """INSERT INTO gpkg_contents
                    (table_name, data_type, identifier, description, last_change, srs_id)
                    VALUES (?, 'attributes', ?, ?, ?, NULL)""",
                (
                    "phase5b_cadastral_status",
                    "Phase 5B cadastral status",
                    "Non-spatial source/status note only; contains no site location or boundary.",
                    stamp,
                ),
            )
            db.commit()
        tables = [row[0] for row in db.execute("SELECT table_name FROM gpkg_contents ORDER BY table_name")]
        after = db.execute("PRAGMA integrity_check").fetchone()[0]
        if after != "ok":
            raise RuntimeError(f"GeoPackage integrity check failed after update: {after}")
        return tables, after


def main() -> None:
    size = annotate_map()
    tables, integrity = add_status_table()
    print(f"Annotated review map: {OUTPUT_MAP.relative_to(ROOT)} ({size[0]} x {size[1]})")
    print(f"GeoPackage tables/layers: {', '.join(tables)}")
    print(f"SQLite integrity: {integrity}")
    print("No geospatial features or coordinates were added.")


if __name__ == "__main__":
    main()
