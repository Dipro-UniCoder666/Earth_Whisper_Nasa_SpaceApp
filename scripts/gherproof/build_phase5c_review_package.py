"""Build a Phase 5C evidence review sheet without inventing site geometry."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "data/gherproof/review/phase5"
GPKG = REVIEW / "pallimangal_phase5_review.gpkg"
SOURCE_MAP = REVIEW / "pallimangal_human_review_map.png"
HISTORICAL_MAP = ROOT / "data/gherproof/reference/historical/beel_bakar_map_figure2_context.png"
PREVIEW_DIR = ROOT / "data/gherproof/reference/dlrs_portal_previews"
MONTAGE = REVIEW / "pallimangal_dlrs_preview_montage.png"
OUTPUT_MAP = REVIEW / "pallimangal_phase5c_review_map.png"
MANIFEST = ROOT / "data/gherproof/manifests/phase5c_official_map_search.json"


def get_font(size: int, bold: bool = False):
    options = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in options:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def preview_montage() -> tuple[int, int]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cards = []
    for record in manifest["map_records"]:
        path = ROOT / record["preview_file"]
        with Image.open(path) as source:
            preview = source.convert("RGB")
        preview.thumbnail((440, 540), Image.Resampling.LANCZOS)
        cards.append((record, preview.copy()))

    width, height = 1500, 1380
    canvas = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 35), "Official DLRS catalogue previews — Sujatpur J.L. 143", font=get_font(48, True), fill=(19, 43, 67))
    draw.text((55, 100), "Low-resolution thumbnails only. Full-resolution CS / RS sheets require purchase.", font=get_font(29), fill=(143, 73, 20))
    x_positions = (65, 790)
    y_positions = (175, 770)
    for idx, (record, preview) in enumerate(cards):
        col, row = idx % 2, idx // 2
        x, y = x_positions[col], y_positions[row]
        label = f"{record['survey_type']} — Sheet {record['sheet_number']} — BDT {record['map_price_bdt']}"
        draw.text((x, y), label, font=get_font(30, True), fill=(29, 56, 83))
        px = x + (630 - preview.width) // 2
        py = y + 45
        draw.rectangle((px - 4, py - 4, px + preview.width + 4, py + preview.height + 4), outline=(148, 161, 174), width=2)
        canvas.paste(preview, (px, py))
    canvas.save(MONTAGE, format="PNG", optimize=True)
    return canvas.size


def compose_review_map() -> tuple[int, int]:
    if not SOURCE_MAP.is_file() or not HISTORICAL_MAP.is_file():
        raise FileNotFoundError("Expected Phase 5B review map and historical Figure 2 crop.")
    with Image.open(SOURCE_MAP) as src:
        current = src.convert("RGB")
    with Image.open(HISTORICAL_MAP) as src:
        context = src.convert("RGB")
    # The source PDF crop includes the start of the printed figure caption;
    # keep only the schematic so the panel does not imply a different label.
    if context.height > 100:
        context = context.crop((0, 0, context.width, context.height - 100))

    width = current.width
    context.thumbnail((width - 220, 2100), Image.Resampling.LANCZOS)
    margin = 60
    status_h = 230
    context_header_h = 210
    context_box_h = context.height + context_header_h + margin * 2
    full_h = current.height + status_h + context_box_h + margin * 2
    canvas = Image.new("RGB", (width, full_h), (255, 255, 255))
    canvas.paste(current, (0, 0))
    draw = ImageDraw.Draw(canvas)

    x = margin
    status_top = current.height + margin // 2
    draw.rounded_rectangle(
        (margin // 2, status_top, width - margin // 2, status_top + status_h),
        radius=24,
        fill=(17, 31, 49),
        outline=(245, 188, 66),
        width=4,
    )
    draw.text((x, status_top + 20), "PHASE 5C DLRS CATALOGUE — NO SITE POSITION ASSERTED", font=get_font(34, True), fill=(255, 255, 255))
    draw.text((x, status_top + 78), "Official catalogue confirms Sujatpur J.L. 143; CS/RS sheets 1 and 2 are listed available/digitized.", font=get_font(24), fill=(235, 241, 248))
    draw.text((x, status_top + 116), "Full-resolution originals require purchase. Preview thumbnails only; no map geometry or target boundary recovered.", font=get_font(24), fill=(235, 241, 248))
    draw.text((x, status_top + 154), "Blue above is Jan 7/19 common-valid radar support over the broad search window, not water or flood extent.", font=get_font(24), fill=(235, 241, 248))

    panel_top = current.height + status_h + margin
    draw.rounded_rectangle(
        (margin // 2, panel_top, width - margin // 2, full_h - margin // 2),
        radius=24,
        fill=(246, 249, 252),
        outline=(67, 103, 137),
        width=4,
    )
    y = panel_top + 22
    draw.text((x, y), "HISTORICAL LOCALITY CONTEXT — NOT A GEOREFERENCED BOUNDARY", font=get_font(38, True), fill=(19, 43, 67))
    y += 62
    draw.text((x, y), "USS / Oxfam Beel Bakar Study, 2014, Figure 2. Schematic labels Sujatpur, Moshihati, Bhaba Daha,", font=get_font(25), fill=(45, 61, 77))
    y += 38
    draw.text((x, y), "Mukteswari River, roads and sluice symbols. It does not locate Pallimangal or prove Beel Kedaria geometry.", font=get_font(25), fill=(45, 61, 77))
    y += 55
    draw.text((x, y), "The historic drawing and the current Sentinel-2/Sentinel-1 panel above are separate, not spatially aligned.", font=get_font(23, True), fill=(153, 66, 38))
    y += 43
    canvas.paste(context, ((width - context.width) // 2, y))
    canvas.save(OUTPUT_MAP, format="PNG", optimize=True)
    return canvas.size


def update_gpkg() -> tuple[list[tuple], str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with sqlite3.connect(GPKG) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"GeoPackage integrity check failed before update: {integrity}")
        contents = {row[0]: row[1] for row in db.execute("SELECT table_name,data_type FROM gpkg_contents")}
        required = {"provisional_search_window": "features", "common_valid_footprint": "features"}
        if not all(contents.get(k) == v for k, v in required.items()):
            raise RuntimeError("Existing Phase 5 feature layers are missing or changed.")

        if "phase5c_dlrs_records" not in contents:
            db.execute(
                """CREATE TABLE phase5c_dlrs_records (
                    fid INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    mouza TEXT NOT NULL,
                    jl_number INTEGER NOT NULL,
                    survey_type TEXT NOT NULL,
                    sheet_number TEXT NOT NULL,
                    status TEXT NOT NULL,
                    is_digitized INTEGER NOT NULL,
                    map_price_bdt INTEGER NOT NULL,
                    delivery_fee_bdt INTEGER NOT NULL,
                    court_fee_bdt INTEGER NOT NULL,
                    preview_path TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    notes TEXT NOT NULL
                )"""
            )
            for item in manifest["map_records"]:
                db.execute(
                    """INSERT INTO phase5c_dlrs_records (
                        record_id,mouza,jl_number,survey_type,sheet_number,status,is_digitized,
                        map_price_bdt,delivery_fee_bdt,court_fee_bdt,preview_path,source_url,notes
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        item["record_id"], "সুজাতপুর", 143, item["survey_type"], item["sheet_number"],
                        item["status"], int(item["is_digitized"]), item["map_price_bdt"],
                        item["delivery_fee_bdt"], item["court_fee_bdt"], item["preview_file"],
                        item["preview_url"], "Low-resolution preview only; full original requires purchase.",
                    ),
                )
            db.execute(
                """INSERT INTO gpkg_contents
                    (table_name,data_type,identifier,description,last_change,srs_id)
                    VALUES ('phase5c_dlrs_records','attributes','Phase 5C DLRS catalogue records',
                    'Non-spatial official catalogue attributes; no parcel geometry.',?,NULL)""",
                (stamp,),
            )

        if "phase5c_historical_context" not in contents:
            db.execute(
                """CREATE TABLE phase5c_historical_context (
                    fid INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_title TEXT NOT NULL,
                    publication_year INTEGER NOT NULL,
                    figure_reference TEXT NOT NULL,
                    labels_observed TEXT NOT NULL,
                    georeferenced INTEGER NOT NULL,
                    target_boundary_supported INTEGER NOT NULL,
                    source_path TEXT NOT NULL,
                    notes TEXT NOT NULL
                )"""
            )
            history = manifest["historical_context_map"]
            db.execute(
                """INSERT INTO phase5c_historical_context (
                    source_title,publication_year,figure_reference,labels_observed,georeferenced,
                    target_boundary_supported,source_path,notes
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    history["title"], 2014, history["figure"], ", ".join(history["labels_visually_observed"]),
                    0, 0, history["derived_context_image"],
                    "Historic schematic context only. Not aligned to the project CRS and not an enclosure or beel boundary.",
                ),
            )
            db.execute(
                """INSERT INTO gpkg_contents
                    (table_name,data_type,identifier,description,last_change,srs_id)
                    VALUES ('phase5c_historical_context','attributes','Phase 5C historical locality context',
                    'Non-spatial source metadata only; no spatial alignment or boundary.',?,NULL)""",
                (stamp,),
            )

        db.commit()
        after = db.execute("PRAGMA integrity_check").fetchone()[0]
        rows = db.execute("SELECT table_name,data_type,srs_id FROM gpkg_contents ORDER BY table_name").fetchall()
        if after != "ok":
            raise RuntimeError(f"GeoPackage integrity check failed after update: {after}")
        if db.execute("SELECT COUNT(*) FROM phase5c_dlrs_records").fetchone()[0] != 4:
            raise RuntimeError("Expected exactly four DLRS catalogue records.")
        if db.execute("SELECT COUNT(*) FROM phase5c_historical_context").fetchone()[0] != 1:
            raise RuntimeError("Expected one historical non-spatial context record.")
        return rows, after


def main() -> None:
    montage_size = preview_montage()
    map_size = compose_review_map()
    layers, integrity = update_gpkg()
    print(f"DLRS preview montage: {MONTAGE.relative_to(ROOT)} {montage_size}")
    print(f"Phase 5C review map: {OUTPUT_MAP.relative_to(ROOT)} {map_size}")
    print(f"GeoPackage contents: {layers}")
    print(f"GeoPackage integrity: {integrity}")
    print("No georeferenced features, candidate geometry or boundary were added.")


if __name__ == "__main__":
    main()
