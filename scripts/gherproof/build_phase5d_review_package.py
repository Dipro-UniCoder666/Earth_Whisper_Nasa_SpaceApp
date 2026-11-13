"""Build Phase 5D secondary-map comparison outputs without adding geometry."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "data/gherproof/review/phase5"
GPKG = REVIEW / "pallimangal_phase5_review.gpkg"
MANIFEST = ROOT / "data/gherproof/manifests/phase5d_free_source_search.json"
OUTPUT = REVIEW / "pallimangal_phase5d_preview_comparison.png"

DLRS = [
    ("Official DLRS CS — Sheet 1", ROOT / "data/gherproof/reference/dlrs_portal_previews/Manirampur_Sujatpur_JL143_CS_sheet1_preview.png"),
    ("Official DLRS CS — Sheet 2", ROOT / "data/gherproof/reference/dlrs_portal_previews/Manirampur_Sujatpur_JL143_CS_sheet2_preview.png"),
    ("Official DLRS RS — Sheet 1", ROOT / "data/gherproof/reference/dlrs_portal_previews/Manirampur_Sujatpur_JL143_RS_sheet1_preview.png"),
    ("Official DLRS RS — Sheet 2", ROOT / "data/gherproof/reference/dlrs_portal_previews/Manirampur_Sujatpur_JL143_RS_sheet2_preview.png"),
]
SECONDARY = ROOT / "data/gherproof/reference/secondary_mouza_sources/mouza_bd_Sujatpur_JL143_BSRS_sheet1_listing_thumbnail.webp"


def font(size: int, bold: bool = False):
    options = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in options:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def build_comparison() -> tuple[int, int]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    width, height = 2200, 1660
    canvas = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 35), "Phase 5D — secondary preview cross-check", font=font(52, True), fill=(19, 43, 67))
    draw.text((55, 105), "No full-resolution secondary sheet recovered; no content match confirmed; no geometry created.", font=font(30), fill=(153, 66, 38))

    # Secondary preview is shown large enough to inspect, with explicit caveats.
    left = (55, 190, 980, 1590)
    draw.rounded_rectangle(left, radius=20, fill=(255, 255, 255), outline=(67, 103, 137), width=3)
    draw.text((85, 220), "Third-party listing preview", font=font(34, True), fill=(19, 43, 67))
    draw.text((85, 268), "Digital Mouza Map · BS/RS · J.L. 143 · Sheet 1 (catalogue claim)", font=font(23), fill=(45, 61, 77))
    with Image.open(SECONDARY) as im:
        preview = im.convert("RGB")
    preview.thumbnail((820, 1000), Image.Resampling.LANCZOS)
    canvas.paste(preview, (left[0] + (left[2] - left[0] - preview.width) // 2, 320))
    draw.text((85, 1370), "Public thumbnail only; product page displayed a fee.", font=font(23), fill=(45, 61, 77))
    draw.text((85, 1410), "Identity and edition remain not_verified; visual match not established.", font=font(23), fill=(153, 66, 38))

    # Four official low-resolution previews occupy a 2 x 2 grid.
    x0, xgap, y0, ygap = 1040, 560, 210, 700
    cell_w, cell_h = 520, 650
    for idx, (label, path) in enumerate(DLRS):
        col, row = idx % 2, idx // 2
        x, y = x0 + col * xgap, y0 + row * ygap
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=16, fill=(255, 255, 255), outline=(148, 161, 174), width=2)
        draw.text((x + 18, y + 18), label, font=font(28, True), fill=(29, 56, 83))
        with Image.open(path) as im:
            official = im.convert("RGB")
        official.thumbnail((420, 560), Image.Resampling.LANCZOS)
        px = x + (cell_w - official.width) // 2
        py = y + 72 + (550 - official.height) // 2
        canvas.paste(official, (px, py))
        draw.text((x + 18, y + cell_h - 50), "DLRS catalogue preview · 227 × 320 px", font=font(20), fill=(77, 91, 104))

    canvas.save(OUTPUT, format="PNG", optimize=True)
    return canvas.size


def update_gpkg() -> tuple[list[tuple], str, int]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with sqlite3.connect(GPKG) as db:
        before = db.execute("PRAGMA integrity_check").fetchone()[0]
        if before != "ok":
            raise RuntimeError(f"GeoPackage integrity failed before update: {before}")
        contents = {r[0]: r[1] for r in db.execute("SELECT table_name,data_type FROM gpkg_contents")}
        if contents.get("provisional_search_window") != "features" or contents.get("common_valid_footprint") != "features":
            raise RuntimeError("Existing Phase 5 geometry layers are missing or changed.")
        if "phase5d_alternative_source_review" not in contents:
            db.execute(
                """CREATE TABLE phase5d_alternative_source_review (
                    record_key TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    survey TEXT NOT NULL,
                    sheet TEXT NOT NULL,
                    jl_number TEXT NOT NULL,
                    source_status TEXT NOT NULL,
                    full_resolution_recovered INTEGER NOT NULL,
                    preview_cross_checked INTEGER NOT NULL,
                    content_match_confirmed INTEGER NOT NULL,
                    notes TEXT NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO gpkg_contents
                    (table_name,data_type,identifier,description,last_change,srs_id)
                    VALUES ('phase5d_alternative_source_review','attributes',
                    'Phase 5D alternative cadastral source review',
                    'Non-spatial review status; no candidate or cadastral geometry.',datetime('now'),NULL)"""
            )
        db.execute("DELETE FROM phase5d_alternative_source_review")
        for sheet in manifest["requested_official_sheets"]:
            db.execute(
                "INSERT INTO phase5d_alternative_source_review VALUES (?,?,?,?,?,?,?,?,?,?)",
                (f"DLRS_{sheet['survey']}_{sheet['sheet']}", "DLRS official catalogue", sheet["survey"], sheet["sheet"], "143", "official_catalogue_confirmed_original_purchase_gated", 0, 1, 0, "Official low-resolution preview compared with the single secondary BS/RS sheet-1 listing thumbnail; no full copy or content match established."),
            )
        db.execute(
            "INSERT INTO phase5d_alternative_source_review VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("MOUSABD_BSRS_1", "Digital Mouza Map / Mouza BD", "BS/RS", "1", "143", "secondary_listing_fee_prompt_full_file_not_accessed_not_verified", 0, 1, 0, "Public listing thumbnail retained for provenance comparison; BDT 80 displayed; no checkout, download or geometry extraction."),
        )
        db.commit()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        rows = db.execute("SELECT table_name,data_type,srs_id FROM gpkg_contents ORDER BY table_name").fetchall()
        count = db.execute("SELECT COUNT(*) FROM phase5d_alternative_source_review").fetchone()[0]
        if integrity != "ok" or count != 5:
            raise RuntimeError(f"GeoPackage Phase 5D validation failed: integrity={integrity}, rows={count}")
        return rows, integrity, count


def main() -> None:
    size = build_comparison()
    tables, integrity, count = update_gpkg()
    print(f"Comparison poster: {OUTPUT.relative_to(ROOT)} {size}")
    print(f"GeoPackage tables: {tables}")
    print(f"GeoPackage integrity: {integrity}; Phase 5D review rows: {count}")
    print("No spatial feature layer, candidate geometry or boundary was added.")


if __name__ == "__main__":
    main()
