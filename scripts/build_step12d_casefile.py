#!/usr/bin/env python3
"""Build the Step 12D Sandhya Earth Event Case File.

The report is assembled only from verified repository outputs.  It replaces the
Step 11 static artifact consumed by the existing read-only case-file endpoint.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from fpdf import FPDF


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STEP2 = ROOT / "step2_nisar_change"
STEP6 = DATA / "step6_feature_engine"
STEP10 = DATA / "step10_ai_investigator"
STEP11 = DATA / "step11_event_case_file"
OUT_PDF = STEP11 / "earth_event_case_file.pdf"
OUT_JSON = STEP11 / "earth_event_case_file.json"
OUT_SOURCES = STEP11 / "sources.txt"
OUT_METHODOLOGY = STEP11 / "methodology.txt"
OUT_FIGURES = STEP11 / "figure_manifest.json"

CYAN = (24, 183, 201)
NAVY = (7, 19, 31)
INK = (28, 43, 58)
MUTED = (92, 111, 128)
LIGHT = (238, 245, 249)
PURPLE = (104, 96, 178)
AMBER = (190, 137, 47)
GREEN = (48, 145, 104)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def f(value, digits=4):
    if value is None or value == "":
        return "Not available"
    return f"{float(value):.{digits}f}"


def pct(value, digits=1):
    if value is None or value == "":
        return "Not available"
    return f"{float(value) * (100 if abs(float(value)) <= 1 else 1):.{digits}f}%"


def clean(value) -> str:
    return str(value).replace("_", " ").replace("—", "-").replace("→", "->")


def split_text(text: str, width: int = 105) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


class Report(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(16, 18, 16)
        self.set_auto_page_break(True, 17)
        self.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf")
        self.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf")
        self.set_title("Earth Whisper - Earth Event Case File - Sandhya River")
        self.set_author("AquaByte / Earth Whisper")
        self.cover_page = True

    def header(self):
        if self.cover_page or self.page_no() == 0:
            return
        self.set_draw_color(*CYAN)
        self.set_line_width(0.35)
        self.line(16, 12, 194, 12)
        self.set_font("Arial", "B", 7)
        self.set_text_color(*CYAN)
        self.cell(0, 6, "EARTH WHISPER  /  SANDHYA INVESTIGATION", 0, 0, "L")
        self.set_text_color(*MUTED)
        self.cell(0, 6, "EARTH EVENT CASE FILE", 0, 1, "R")
        self.ln(5)

    def footer(self):
        if self.cover_page:
            return
        self.set_y(-12)
        self.set_draw_color(210, 220, 226)
        self.line(16, self.get_y(), 194, self.get_y())
        self.set_font("Arial", "", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 7, "Sandhya Investigation  |  Verified Earth Whisper evidence", 0, 0, "L")
        self.cell(0, 7, f"Page {self.page_no()}", 0, 0, "R")

    def add_report_page(self, title: str, kicker: str = ""):
        self.cover_page = False
        self.add_page()
        self.section(title, kicker)

    def section(self, title: str, kicker: str = ""):
        if kicker:
            self.set_font("Arial", "B", 8)
            self.set_text_color(*CYAN)
            self.cell(0, 5, kicker.upper(), 0, 1)
        self.set_font("Arial", "B", 19)
        self.set_text_color(*INK)
        self.multi_cell(0, 8, title, align="L")
        self.set_draw_color(*CYAN)
        self.set_line_width(0.7)
        self.line(16, self.get_y() + 2, 64, self.get_y() + 2)
        self.ln(7)

    def h2(self, text: str):
        self.set_font("Arial", "B", 12)
        self.set_text_color(*INK)
        self.ln(3)
        self.multi_cell(0, 6, text)
        self.set_draw_color(210, 220, 226)
        self.set_line_width(0.25)
        self.line(16, self.get_y() + 1, 194, self.get_y() + 1)
        self.ln(4)

    def paragraph(self, text: str, size=9.5, color=INK, gap=2):
        self.set_font("Arial", "", size)
        self.set_text_color(*color)
        self.multi_cell(0, 5, clean(text), align="L")
        self.ln(gap)

    def bullet_list(self, items: Iterable[str], color=INK):
        for item in items:
            self.set_x(21)
            self.set_font("Arial", "", 9)
            self.set_text_color(*color)
            self.cell(4, 5, "-")
            self.multi_cell(169, 5, clean(item), align="L")
            self.ln(1)

    def callout(self, title: str, text: str, color=CYAN):
        x, y = self.get_x(), self.get_y()
        lines = split_text(text, 105)
        h = 12 + len(lines) * 4.5
        self.set_fill_color(244, 249, 251)
        self.set_draw_color(*color)
        self.set_line_width(0.8)
        self.rect(x, y, 178, h, "DF")
        self.set_xy(x + 5, y + 4)
        self.set_font("Arial", "B", 8)
        self.set_text_color(*color)
        self.cell(168, 4, title.upper(), 0, 1)
        self.set_x(x + 5)
        self.set_font("Arial", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(168, 4.5, clean(text), align="L")
        self.set_y(y + h + 5)

    def table(self, headers: Sequence[str], rows: Sequence[Sequence[str]], widths: Sequence[float], font=7.5):
        def row(values, header=False):
            height = 6 if header else 5.5
            if self.get_y() + height > 277:
                self.add_page(self.cur_orientation)
            self.set_fill_color(*(NAVY if header else (246, 249, 251)))
            self.set_text_color(*(LIGHT if header else INK))
            self.set_font("Arial", "B" if header else "", font if not header else max(font - 0.3, 6.5))
            for value, width in zip(values, widths):
                self.cell(width, height, clean(value)[:45], 1, 0, "L", True)
            self.ln(height)

        row(headers, True)
        for values in rows:
            row(values)
        self.ln(3)

    def metric_grid(self, metrics: Sequence[tuple[str, str]], cols=2):
        width = 178 / cols
        for index in range(0, len(metrics), cols):
            batch = metrics[index:index + cols]
            y = self.get_y()
            height = 18
            for col, (label, value) in enumerate(batch):
                x = 16 + col * width
                self.set_fill_color(244, 249, 251)
                self.set_draw_color(214, 225, 231)
                self.rect(x, y, width - 3, height, "DF")
                self.set_xy(x + 4, y + 3)
                self.set_font("Arial", "B", 7)
                self.set_text_color(*CYAN)
                self.cell(width - 10, 4, label.upper(), 0, 1)
                self.set_x(x + 4)
                self.set_font("Arial", "B", 11)
                self.set_text_color(*INK)
                self.cell(width - 10, 6, clean(value), 0, 0)
            self.set_y(y + height + 4)

    def bar_chart(self, labels: Sequence[str], values: Sequence[float], unit=""):
        max_value = max(values) if values else 1
        x0, y0, chart_w, chart_h = 28, self.get_y() + 2, 145, 42
        self.set_draw_color(190, 205, 213)
        self.line(x0, y0 + chart_h, x0 + chart_w, y0 + chart_h)
        bar_w = chart_w / max(len(values), 1) * 0.58
        for i, (label, value) in enumerate(zip(labels, values)):
            x = x0 + (i + 0.5) * chart_w / len(values) - bar_w / 2
            h = max(2, chart_h * value / max_value)
            self.set_fill_color(*CYAN)
            self.rect(x, y0 + chart_h - h, bar_w, h, "F")
            self.set_xy(x - 10, y0 + chart_h + 2)
            self.set_font("Arial", "", 7)
            self.set_text_color(*MUTED)
            self.cell(bar_w + 20, 4, label, 0, 0, "C")
            self.set_xy(x - 12, y0 + chart_h - h - 7)
            self.set_font("Arial", "B", 7)
            self.set_text_color(*INK)
            self.cell(bar_w + 24, 4, f"{value:.2f}{unit}", 0, 0, "C")
        self.set_y(y0 + chart_h + 12)

    def pipeline(self, steps: Sequence[str]):
        y = self.get_y()
        for index, step in enumerate(steps):
            x = 23 + (index % 2) * 91
            if index and index % 2 == 0:
                y += 20
            self.set_fill_color(242, 248, 250)
            self.set_draw_color(*CYAN)
            self.rect(x, y, 76, 12, "DF")
            self.set_xy(x + 3, y + 3)
            self.set_font("Arial", "B", 8)
            self.set_text_color(*INK)
            self.cell(70, 5, step.upper(), 0, 0, "C")
            if index < len(steps) - 1:
                if index % 2 == 0:
                    self.set_xy(x + 76, y + 3)
                    self.set_text_color(*CYAN)
                    self.cell(15, 5, "->", 0, 0, "C")
                else:
                    self.set_xy(101, y + 13)
                    self.set_text_color(*CYAN)
                    self.cell(8, 5, "v", 0, 0, "C")
        self.set_y(y + 26)


def build_stats():
    stats = {}
    for key, filename in {
        "HH_023_to_029": "HH_023_to_029_coherence_change_exact_aoi.npy",
        "VV_025_to_026": "VV_025_to_026_coherence_change_exact_aoi.npy",
    }.items():
        values = np.load(STEP2 / filename)
        values = values[np.isfinite(values)]
        stats[key] = {
            "valid_pixels": int(values.size),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "p05": float(np.percentile(values, 5)),
            "p25": float(np.percentile(values, 25)),
            "p75": float(np.percentile(values, 75)),
            "p95": float(np.percentile(values, 95)),
            "le_-0.10_pct": float(np.mean(values <= -0.10) * 100),
            "le_-0.20_pct": float(np.mean(values <= -0.20) * 100),
            "le_-0.30_pct": float(np.mean(values <= -0.30) * 100),
        }
    return stats


def build_json(contract, previous, stats):
    sources = [
        {"name": "NISAR Data User Guide", "url": "https://nisar-docs.asf.alaska.edu/"},
        {"name": "NISAR GUNW Product Documentation", "url": "https://nisar-docs.asf.alaska.edu/gunw/"},
        {"name": "NISAR Vertex Search", "url": "https://nisar-docs.asf.alaska.edu/vertex/"},
        {"name": "ASF Vertex", "url": "https://vertex-plus.asf.alaska.edu/"},
        {"name": "NISAR Product Overview", "url": "https://nisar-docs.asf.alaska.edu/products-overview/"},
        {"name": "HLS / Harmonized Landsat Sentinel-2", "url": "https://www.earthdata.nasa.gov/data/projects/hls"},
        {"name": "NASA GPM / IMERG", "url": "https://gpm.nasa.gov/data/imerg"},
        {"name": "NASA Earthdata", "url": "https://www.earthdata.nasa.gov/"},
    ]
    out = dict(previous)
    out.update({
        "schema_version": "12D",
        "case_file_id": "Sandhya Investigation",
        "aoi_details": {
            "center": {"latitude": 22.4900, "longitude": 90.1850},
            "wkt": contract["aoi"]["wkt"],
            "bounds": {"west": 90.15, "south": 22.47, "east": 90.22, "north": 22.51},
            "utm_epsg": "EPSG:32646",
            "rectangular_window": {"columns": "5584:5948", "rows": "9928:10157", "width": 364, "height": 229, "pixels": 83356},
            "exact_aoi_pixels": 79874,
            "outside_aoi_pixels": 3482,
            "retention_percent": 95.822736,
        },
        "nisar_change_statistics": stats,
        "nisar_observations": [
            {"product": "GUNW_023_091", "dates": "20 Jun 2026 -> 02 Jul 2026", "track": 91, "frame": 77, "orbit": "Descending", "polarization": "HH"},
            {"product": "GUNW_025_091", "dates": "14 Jul 2026 -> 31 Aug 2026", "track": 91, "frame": 77, "orbit": "Descending", "polarization": "VV"},
            {"product": "GUNW_026_091", "dates": "26 Jul 2026 -> 19 Aug 2026", "track": 91, "frame": 77, "orbit": "Descending", "polarization": "VV"},
            {"product": "GUNW_029_091", "dates": "31 Aug 2026 -> 12 Sep 2026", "track": 91, "frame": 77, "orbit": "Descending", "polarization": "HH"},
        ],
        "candidate_detection": {"threshold": "delta coherence <= -0.20", "minimum_connected_region_pixels": 10, "connectivity": "8-connected", "pixel_area_m2": 400, "candidate_regions": 211},
        "sentinel1_aoi_crosscheck": {"search_period": "June-September 2026", "platform": "S1D", "dates": "03 Jul 2026 -> 15 Jul 2026", "interval_days": 12, "path": 150, "frame": 519, "valid_pixels_each": 1120000, "mean_db": {"03 Jul 2026": -10.1987, "15 Jul 2026": -10.6597, "change": -0.46}, "median_db": {"03 Jul 2026": -9.1307, "15 Jul 2026": -9.5977, "change": -0.47}, "candidate_overlap": "211/211"},
        "ml_analysis": {"purpose": "Unsupervised statistical anomaly detection and investigation prioritization", "features": ["s1_median_db", "s1_min_db", "s1_max_db", "s1_pct_le_minus3db"], "comparison_groups": {"HH": 195, "VV": 16}, "knn_k": [3, 5, 8], "investigated_candidates": 32, "investigated_breakdown": {"HH": 29, "VV": 3}},
        "cross_radar_distribution": {"dual_radar_upper_quartile_stable": 11, "dual_radar_upper_quartile_but_sensitive": 5, "nisar_upper_quartile_s1_not_upper_quartile": 38, "s1_upper_quartile_nisar_not_upper_quartile": 34, "s1_upper_quartile_but_sensitive": 6, "neither_radar_measurement_upper_quartile": 117},
        "optical_verification": {"dataset": "HLS S30 v2.0", "tile": "T46QBK", "dates": ["26 Jun 2026", "14 Sep 2026"], "tested_candidates": 6, "tested_status": "TESTED - INCONCLUSIVE", "not_tested_candidates": 205, "valid_pixels": 0, "note": "High aerosol conditions severely limited valid optical coverage."},
        "rainfall_context": {"dataset": "NASA GPM IMERG Late Run V07", "short_name": "GPM_3IMERGDL", "date": "12 Sep 2026", "three_day_mm": 13.056936, "seven_day_mm": 32.511207, "fourteen_day_mm": 131.931329, "maximum_daily_mm": 42.598942, "wet_days_gt5mm": 9, "gunw_023_14day": None, "role": "Environmental context only"},
        "sources_and_references": sources,
        "methodology_steps": ["NISAR coverage", "NISAR AOI extraction and change", "Temporal fingerprint", "Optical verification", "Environmental context", "Feature engine", "ML anomaly detection", "Evidence fusion", "Uncertainty", "AI Investigator", "Event Case File"],
        "figure_manifest": [
            {"file": "step2_nisar_change/HH_023_to_029_coherence_change.png", "title": "NISAR HH coherence-change map", "source": "Earth Whisper Step 2 - exact AOI output"},
            {"file": "step2_nisar_change/VV_025_to_026_coherence_change.png", "title": "NISAR VV coherence-change map", "source": "Earth Whisper Step 2 - exact AOI output"},
        ],
        "all_candidate_records": contract["candidates"],
    })
    return out


def build_report(contract, case_doc, stats):
    report = Report()
    report.cover_page = True
    report.add_page()
    report.set_fill_color(*NAVY)
    report.rect(0, 0, 210, 297, "F")
    report.set_text_color(*CYAN)
    report.set_font("Arial", "B", 13)
    report.set_xy(22, 42)
    report.cell(165, 8, "EARTH WHISPER", 0, 1)
    report.set_text_color(*LIGHT)
    report.set_font("Arial", "B", 28)
    report.cell(165, 13, "EARTH EVENT CASE FILE", 0, 1)
    report.set_draw_color(*CYAN)
    report.set_line_width(1.2)
    report.line(22, 70, 80, 70)
    report.set_xy(22, 103)
    report.set_font("Arial", "B", 20)
    report.multi_cell(165, 10, "Sandhya River near Babuganj, Barishal, Bangladesh", align="L")
    report.set_font("Arial", "", 11)
    report.set_text_color(178, 205, 218)
    report.ln(5)
    report.cell(165, 7, "22.4900 N  |  90.1850 E", 0, 1)
    report.cell(165, 7, "AOI CENTER", 0, 1)
    report.cell(165, 7, "Investigation period: June-September 2026", 0, 1)
    report.cell(165, 7, "Case File ID: Sandhya Investigation", 0, 1)
    report.set_xy(22, 253)
    report.set_font("Arial", "", 9)
    report.set_text_color(139, 171, 188)
    report.multi_cell(160, 5, "Verified evidence dossier\nNISAR | Sentinel-1 | HLS | GPM IMERG | comparison-aware anomaly analysis", align="L")

    report.add_report_page("Executive Summary", "01")
    report.metric_grid([
        ("Location", "Sandhya River near Babuganj"),
        ("AOI center", "22.4900 N / 90.1850 E"),
        ("Investigation period", "June-September 2026"),
        ("Primary observation", "NISAR interferometric radar"),
        ("Supporting radar", "Sentinel-1"),
        ("Optical verification", "Tested - inconclusive / many not tested"),
        ("Environmental context", "GPM IMERG rainfall"),
        ("Ground truth", "Not available"),
    ])
    report.callout("Scientific finding", "Earth Whisper detected localized changes in NISAR radar coherence within the Sandhya AOI and used Sentinel-1, temporal observations, rainfall context, optical screening, and statistical anomaly analysis to prioritize candidate regions for investigation. The evidence identifies radar-signal anomalies, but does not by itself establish a specific physical cause such as erosion, flooding, or bank migration.")
    report.h2("Evidence language")
    report.paragraph("This case file separates direct observations, independent radar cross-checks, environmental context, statistical unusualness, and missing or inconclusive evidence. The ML stage prioritizes unusual feature patterns; it is not a physical-cause classifier or an AI prediction.")

    report.add_report_page("Investigation Location and Exact AOI", "02")
    report.metric_grid([("AOI", "Sandhya River near Babuganj"), ("Center", "22.4900 N / 90.1850 E"), ("UTM", "EPSG:32646"), ("Retention", "95.822736%")])
    report.h2("Geometry")
    report.paragraph("The investigation used a fixed AOI around the Sandhya River near Babuganj, Barishal. Candidate-region statistics were calculated with the exact AOI mask rather than treating the full rectangular extraction as the AOI.")
    report.table(["Field", "Verified value"], [
        ["AOI WKT", contract["aoi"]["wkt"]],
        ["Bounds", "90.15 to 90.22 E; 22.47 to 22.51 N"],
        ["Extraction window", "Columns 5584:5948; rows 9928:10157"],
        ["Rectangular window", "364 x 229 pixels = 83,356 pixels"],
        ["Exact AOI retained", "79,874 pixels"],
        ["Outside exact AOI", "3,482 pixels"],
    ], [42, 136])

    report.add_report_page("Investigation Pipeline", "03")
    report.paragraph("Earth Whisper is a multi-stage evidence workflow. The case file is not a direct NISAR-to-AI answer: each later stage consumes outputs from the earlier verified processing stage.")
    report.pipeline(["NISAR", "Exact AOI extraction", "Radar change detection", "Temporal fingerprint", "Sentinel-1 cross-check", "Optical verification", "Rainfall context", "Feature engineering", "ML anomaly analysis", "Evidence fusion", "Candidate investigation", "Earth Event Case File"])
    report.callout("Interpretation boundary", "Deterministic scientific processing produced the measurements. The comparison-aware ML stage identified statistically unusual candidate feature patterns, and the AI Investigator organized verified evidence for review. Neither stage establishes a physical event by itself.", PURPLE)

    report.add_report_page("NISAR Dataset and Observations", "04")
    report.paragraph("GUNW products provide the primary interferometric coherence observations used in this investigation. GSLC supports radar amplitude/backscatter characterization, and GCOV is available as a NISAR surface/backscatter/polarimetric product. The products are not treated as interchangeable or equally decisive in the final evidence statement.")
    report.table(["Product", "Role in this investigation"], [
        ["GUNW", "Primary interferometric evidence for coherence observations."],
        ["GSLC", "Radar amplitude/backscatter characterization."],
        ["GCOV", "NISAR surface/backscatter/polarimetric data product available in the project."],
    ], [34, 144])
    report.h2("Four key GUNW observations")
    report.table(["Product", "Dates", "Track / frame", "Orbit", "Polarization"], [
        ["GUNW_023_091", "20 Jun -> 02 Jul 2026", "91 / 77", "Descending", "HH"],
        ["GUNW_025_091", "14 Jul -> 31 Aug 2026", "91 / 77", "Descending", "VV"],
        ["GUNW_026_091", "26 Jul -> 19 Aug 2026", "91 / 77", "Descending", "VV"],
        ["GUNW_029_091", "31 Aug -> 12 Sep 2026", "91 / 77", "Descending", "HH"],
    ], [32, 55, 29, 31, 31])
    report.callout("Scientific note", "These are separate interferometric observation pairs with different temporal baselines and polarizations. They are not one uniform, continuous same-polarization coherence time series. The 025 and 029 observations share 31 Aug as a connected acquisition date, but the full set remains a grouped evidence fingerprint.", AMBER)

    for label, title in [("HH_023_to_029", "HH 023 -> 029"), ("VV_025_to_026", "VV 025 -> 026")]:
        report.add_report_page("NISAR Coherence Change - " + title, "05")
        item = stats[label]
        report.h2(title)
        report.metric_grid([("Valid pixels", f"{item['valid_pixels']:,}"), ("Mean", f(item['mean'], 9)), ("Median", f(item['median'], 9)), ("P05 / P95", f"{f(item['p05'], 5)} / {f(item['p95'], 5)}")])
        report.table(["Statistic", "Value", "Statistic", "Value"], [
            ["P25", f(item["p25"], 8), "P75", f(item["p75"], 8)],
            ["Pixels <= -0.10", f"{item['le_-0.10_pct']:.4f}%", "Pixels <= -0.20", f"{item['le_-0.20_pct']:.4f}%"],
            ["Pixels <= -0.30", f"{item['le_-0.30_pct']:.4f}%", "Source", "Exact AOI NPY output"],
        ], [42, 47, 50, 39])
        report.bar_chart(["<= -0.10", "<= -0.20", "<= -0.30"], [item["le_-0.10_pct"], item["le_-0.20_pct"], item["le_-0.30_pct"]], "%")
        report.paragraph(("The HH comparison shows a negative mean and median across the exact AOI. The distribution is reported separately from VV and is not combined with it." if label == "HH_023_to_029" else "The VV comparison has a positive AOI mean and median while still containing a lower-tail population of negative changes. HH and VV distributions are reported separately and are not combined."), color=MUTED)

    report.add_report_page("Verified NISAR Figures", "06")
    figures = [
        (STEP2 / "HH_023_to_029_coherence_change.png", "Figure 1 - NISAR HH coherence-change map", "20 Jun 2026 -> 02 Jul 2026 / 31 Aug 2026 -> 12 Sep 2026; HH polarization"),
        (STEP2 / "VV_025_to_026_coherence_change.png", "Figure 2 - NISAR VV coherence-change map", "14 Jul 2026 -> 31 Aug 2026 / 26 Jul 2026 -> 19 Aug 2026; VV polarization"),
    ]
    for figure_index, (image, title, detail) in enumerate(figures):
        if image.exists():
            if figure_index == 1:
                report.add_report_page("Verified NISAR Figures - Continued", "06")
            report.h2(title)
            report.image(str(image), x=25, w=160)
            report.ln(3)
            report.set_font("Arial", "B", 8)
            report.set_text_color(*CYAN)
            report.cell(0, 4, "Source: Earth Whisper Step 2 - verified exact-AOI output", 0, 1)
            report.paragraph(detail + ". Negative values indicate lower coherence in the later observation under the comparison. This is a radar-signal change indicator, not proof of a specific physical process.", size=8.5, color=MUTED)
    report.callout("Figure caveat", "The maps show derived coherence-change indicators within the Sandhya investigation area. They must not be labeled as erosion maps, landslide maps, or flood maps without independent evidence that establishes such a physical cause.", AMBER)

    report.add_report_page("Candidate Region Detection", "07")
    report.paragraph("Candidate generation used a NISAR coherence-change threshold of delta coherence <= -0.20, a minimum connected region of 10 pixels, 8-connected components, and a 400 m2 pixel area. The resulting 211 records represent spatially connected threshold-exceeding regions, not confirmed events.")
    report.metric_grid([("Candidate records", "211"), ("HH comparison", "195"), ("VV comparison", "16"), ("Pixel area", "400 m2"), ("Connectivity", "8-connected"), ("Threshold", "delta coherence <= -0.20")])
    report.h2("Candidate interpretation")
    report.callout("Selection boundary", "The candidate pool was generated from NISAR change detection and is not an unbiased sample of every location in the AOI. Later Sentinel-1, optical, rainfall, and statistical stages evaluate or contextualize this selected pool.", AMBER)

    report.add_report_page("Temporal Fingerprint", "08")
    report.paragraph("The temporal fingerprint uses four separate interferometric pairs. For the selected investigation set, coherence values are preserved in the machine-readable case file and in the candidate records below. The pairs are shown as grouped observations rather than one connected time-series line.")
    report.table(["Pair", "Dates", "Polarization", "Interpretation"], [
        ["01", "20 Jun -> 02 Jul 2026", "HH", "Separate interferometric pair"],
        ["02", "14 Jul -> 31 Aug 2026", "VV", "Separate interferometric pair"],
        ["03", "26 Jul -> 19 Aug 2026", "VV", "Separate interferometric pair"],
        ["04", "31 Aug -> 12 Sep 2026", "HH", "Separate interferometric pair"],
    ], [18, 58, 28, 74])
    report.h2("Representative investigated candidates")
    temporal_rows = []
    for case in case_doc["cases"][:8]:
        evidence = case["evidence"]["nisar"]
        temporal_rows.append([str(case["region_id"]), case["comparison"].split("_")[0], f(case["area_m2"], 0) + " m2", clean(evidence["gunw_measurements"])[:90]])
    report.table(["Region", "Pol", "Area", "Verified NISAR measurements"], temporal_rows, [25, 22, 28, 103], 7)
    report.paragraph("Different interferometric pairs and polarizations are shown separately. A candidate-level technical record is retained in the JSON appendix for all 32 investigated candidates.", size=8.5, color=MUTED)

    report.add_report_page("Sentinel-1 Cross-check", "09")
    report.paragraph("Sentinel-1 provides an additional radar observation with a different acquisition history and measurement behavior. It is a cross-check of NISAR-selected candidate regions, not independent ground truth.")
    report.table(["Field", "Verified value"], [
        ["Search period", "June-September 2026"],
        ["Same-platform pair", "S1D: 03 Jul 2026 -> 15 Jul 2026 (12 days)"],
        ["Path / frame", "Full Path 150 / Frame 519"],
        ["Valid pixels each", "1,120,000"],
        ["Mean dB", "-10.1987 -> -10.6597; change about -0.46 dB"],
        ["Median dB", "-9.1307 -> -9.5977; change about -0.47 dB"],
        ["Candidate overlap", "211 / 211 NISAR candidates"],
    ], [45, 133])
    report.callout("Cross-check meaning", "Sentinel-1 provides an additional radar view of the observed change. Candidate-level agreement can support prioritization, but it does not prove erosion, flooding, bank migration, or another physical event.", PURPLE)

    report.add_report_page("ML and Cross-radar Consistency", "10")
    report.h2("Comparison-aware statistical anomaly analysis")
    report.paragraph("The ML stage identifies candidate regions whose Sentinel-1 feature patterns are statistically unusual compared with other candidates in the same comparison group. It is unsupervised statistical anomaly detection, not erosion classification, event probability, physical-cause classification, ground truth, or AI confidence.")
    report.table(["Input features", "Comparison groups", "k values", "Selection output"], [["s1_median_db; s1_min_db; s1_max_db; s1_pct_le_minus3db", "HH: 195 | VV: 16", "3, 5, 8", "Top 20 by anomaly percentile plus stable/sensitive dual-radar cases"],], [72, 38, 24, 44], 7)
    report.paragraph("Redundant features were excluded after feature-correlation analysis. Separate HH and VV populations are used because their distributions differ and should not be treated as one homogeneous population.")
    report.h2("Cross-radar distribution")
    report.table(["Category", "Count"], [
        ["Dual-radar upper-quartile stable", "11"],
        ["Dual-radar upper-quartile but sensitive", "5"],
        ["NISAR upper-quartile; S1 not upper-quartile", "38"],
        ["S1 upper-quartile; NISAR not upper-quartile", "34"],
        ["S1 upper-quartile but sensitive", "6"],
        ["Neither radar measurement upper-quartile", "117"],
    ], [142, 36])
    report.callout("Statistical boundary", "These categories describe statistical consistency within comparison populations. They are not physical-event probabilities and should not be converted into a confidence percentage.", AMBER)

    report.add_report_page("Optical Verification and Rainfall Context", "11")
    report.h2("Optical verification")
    report.table(["Field", "Verified value"], [
        ["Dataset", "HLS S30 v2.0"], ["Tile", "T46QBK"], ["Selected dates", "26 Jun 2026; 14 Sep 2026"], ["Screened candidates", "6"], ["Status", "TESTED - INCONCLUSIVE"], ["Not screened", "205 candidates"], ["Valid optical pixels", "0 for the inconclusive tested cases"],
    ], [48, 130])
    report.paragraph("Optical verification was inconclusive because valid optical coverage was severely limited by high aerosol conditions. Candidates not screened remain NOT TESTED. No NDVI, NDWI, MNDWI, water extent, or optical confirmation is fabricated in this report.")
    report.h2("Rainfall / environmental context")
    rain = contract["dashboard_summary"]["rainfall_context"]
    report.bar_chart(["3-day", "7-day", "14-day", "max daily"], [rain["three_day_mm"], rain["seven_day_mm"], rain["fourteen_day_mm"], rain["maximum_daily_mm"]], " mm")
    report.table(["Context", "Value"], [["Dataset", "NASA GPM IMERG Late Run V07 / GPM_3IMERGDL"], ["12 Sep 2026, 3-day", f"{rain['three_day_mm']:.6f} mm"], ["12 Sep 2026, 7-day", f"{rain['seven_day_mm']:.6f} mm"], ["12 Sep 2026, 14-day", f"{rain['fourteen_day_mm']:.6f} mm"], ["Maximum daily", f"{rain['maximum_daily_mm']:.6f} mm"], ["Wet days > 5 mm", str(rain["wet_days_gt_5mm"])],], [58, 120], 8)
    report.paragraph("Rainfall is environmental context and does not establish that rainfall caused the radar anomaly. The 14-day context for GUNW_023 is unavailable. For GUNW_025, the 31 Aug rainfall is end-date context for the 14 Jul -> 31 Aug interval, not rainfall across the full 48-day interval.", color=MUTED)

    report.add_report_page("AI Investigator and Investigated Candidates", "12")
    report.paragraph("The AI Investigator interpreted verified evidence that had already been produced by deterministic processing and ML analysis. It did not discover or recalculate the original satellite signal. The selection included the top 20 candidates by comparison-aware anomaly percentile plus all candidates in stable or sensitive dual-radar upper-quartile categories. After deduplication: 32 investigated candidates, 29 HH and 3 VV.")
    report.table(["Order", "Pol", "Region", "Area m2", "Location", "NISAR", "S1 median", "ML percentile"], [
        [str(i + 1), c["comparison"].split("_")[0], str(c["region_id"]), f(c["area_m2"], 0), f"{c['location']['lat']:.4f}, {c['location']['lon']:.4f}", f(c["evidence"]["nisar"]["nisar_change"], 3), f(c["evidence"]["sentinel1"]["s1_median_db"], 2), pct(c["evidence"]["sentinel1"]["s1_anomaly_percentile"], 1)]
        for i, c in enumerate(case_doc["cases"])
    ], [14, 12, 20, 22, 46, 20, 22, 22], 6.5)
    report.paragraph("The complete candidate keys, feature values, cross-radar categories, optical states, rainfall context, uncertainty, and provenance are preserved in the structured JSON case file. Region numbers in this table are readable labels; the technical identity rule remains comparison + region_id.", size=8.5, color=MUTED)

    report.add_report_page("Evidence Fusion and Candidate Case Studies", "13")
    report.h2("Evidence matrix")
    report.table(["Layer", "Role", "Status"], [
        ["NISAR", "Primary radar coherence evidence", "Available / supporting"],
        ["Sentinel-1", "Additional radar observation", "Available / supporting cross-check"],
        ["Optical", "HLS screening", "Tested - inconclusive or not tested"],
        ["Rainfall", "Regional environmental context", "Available / context only"],
        ["Statistical model", "Comparison-aware kNN unusualness", "Prioritization / uncertain with k-sensitivity"],
        ["Ground truth", "Independent physical-event label", "Not available"],
    ], [34, 83, 61])
    report.h2("Selected candidate case studies")
    for case in case_doc["cases"][:4]:
        nisar = case["evidence"]["nisar"]
        s1 = case["evidence"]["sentinel1"]
        report.set_font("Arial", "B", 9)
        report.set_text_color(*CYAN)
        report.cell(0, 5, f"Region {case['region_id']} - {case['comparison'].split('_')[0]} - {case['area_m2']:.0f} m2", 0, 1)
        report.paragraph(f"Location {case['location']['lat']:.5f}, {case['location']['lon']:.5f}. NISAR change {nisar['nisar_change']:.4f}; Sentinel-1 median change {s1['s1_median_db']:.2f} dB; ML anomaly percentile {s1['s1_anomaly_percentile'] * 100:.1f}%; cross-radar status {clean(s1['cross_radar_status'])}; optical status {clean(case['evidence']['optical']['optical_evidence_status'])}. Physical cause remains unresolved.", size=8.5, gap=3)

    report.add_report_page("Uncertainty, Limitations, and Final Finding", "14")
    report.h2("Major limitations")
    report.bullet_list([
        "NISAR GUNW observations are interferometric measurements over specific acquisition pairs, not one continuous deformation time series.",
        "Temporal baselines and HH/VV polarizations differ and are not combined.",
        "Sentinel-1 is a cross-check sampled around NISAR-selected candidates, not independent ground truth.",
        "Only 6 of 211 candidates were optically tested; all tested cases were inconclusive and 205 were not tested.",
        "High aerosol conditions limited optical verification and no valid optical pixels were available for several windows.",
        "GPM IMERG rainfall is coarser than the AOI and is context only; early GUNW_023 14-day context is unavailable.",
        "Candidate detection depends on the change threshold and connected-region rules.",
        "ML anomaly values identify statistical unusualness and can vary with neighbourhood size; HH has 195 candidates and VV has 16.",
        "No independent ground-truth labels are available, so no physical event or calibrated physical-event probability can be confirmed.",
    ])
    report.callout("Earth Whisper finding", "Earth Whisper identified spatially localized radar-signal changes within the Sandhya investigation AOI. The strongest candidate regions were prioritized using comparison-aware statistical anomaly analysis and cross-radar evidence. Sentinel-1 provides additional radar observations, optical verification was limited or inconclusive, and rainfall provides environmental context without establishing causation. Without independent ground truth or conclusive optical evidence, the physical cause of the radar changes remains unresolved.")

    report.add_report_page("Data Sources and Methodology", "15")
    report.h2("Official references")
    links = [
        ("NISAR Data User Guide", "https://nisar-docs.asf.alaska.edu/"),
        ("NISAR GUNW Product Documentation", "https://nisar-docs.asf.alaska.edu/gunw/"),
        ("NISAR Vertex Search", "https://nisar-docs.asf.alaska.edu/vertex/"),
        ("ASF Vertex", "https://vertex-plus.asf.alaska.edu/"),
        ("NISAR Product Overview", "https://nisar-docs.asf.alaska.edu/products-overview/"),
        ("HLS / Harmonized Landsat Sentinel-2", "https://www.earthdata.nasa.gov/data/projects/hls"),
        ("NASA GPM / IMERG", "https://gpm.nasa.gov/data/imerg"),
        ("NASA Earthdata", "https://www.earthdata.nasa.gov/"),
    ]
    for label, url in links:
        report.set_font("Arial", "B", 8.5)
        report.set_text_color(*CYAN)
        report.write(5, label + ": ", link=url)
        report.set_font("Arial", "", 8.5)
        report.set_text_color(*MUTED)
        report.write(5, url, link=url)
        report.ln(6)
    report.h2("Methodology reference")
    report.table(["Step", "Readable methodology"], [[str(i + 1), value] for i, value in enumerate([
        "NISAR coverage", "NISAR AOI extraction and change", "Temporal fingerprint", "Optical verification", "Environmental context", "Feature engine", "ML anomaly detection", "Evidence fusion", "Uncertainty", "AI Investigator", "Event Case File",
    ])], [18, 160], 8)
    report.paragraph("Source traceability: Earth Whisper Step 2 exact-AOI NPY/PNG outputs; Step 3-6 feature and context tables; Step 8 comparison-aware anomaly and cross-radar outputs; Step 9 uncertainty annotations; Step 10 investigated candidate CSV/manifest; and Step 11 case-file JSON. The machine-readable appendix preserves the full source-record fields.", size=8.5, color=MUTED)

    return report


def main():
    contract = read_json(DATA / "step12_backend" / "earth_whisper_candidates.json")
    previous = read_json(OUT_JSON)
    stats = build_stats()
    updated = build_json(contract, previous, stats)
    OUT_JSON.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = build_report(contract, previous, stats)
    report.output(str(OUT_PDF))
    figure_manifest = updated["figure_manifest"]
    OUT_FIGURES.write_text(json.dumps({"figures": figure_manifest}, indent=2) + "\n", encoding="utf-8")
    OUT_SOURCES.write_text("\n".join(f"{name}: {url}" for name, url in [
        ("NISAR Data User Guide", "https://nisar-docs.asf.alaska.edu/"),
        ("NISAR GUNW Product Documentation", "https://nisar-docs.asf.alaska.edu/gunw/"),
        ("NISAR Vertex Search", "https://nisar-docs.asf.alaska.edu/vertex/"),
        ("ASF Vertex", "https://vertex-plus.asf.alaska.edu/"),
        ("NISAR Product Overview", "https://nisar-docs.asf.alaska.edu/products-overview/"),
        ("HLS", "https://www.earthdata.nasa.gov/data/projects/hls"),
        ("NASA GPM IMERG", "https://gpm.nasa.gov/data/imerg"),
        ("NASA Earthdata", "https://www.earthdata.nasa.gov/"),
    ]) + "\n", encoding="utf-8")
    OUT_METHODOLOGY.write_text("\n".join(f"Step {i + 1}: {step}" for i, step in enumerate(updated["methodology_steps"])) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size:,} bytes)")
    print(f"Wrote {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes)")
    print(f"Cases preserved: {len(updated['cases'])}; all candidate records: {len(updated['all_candidate_records'])}")


if __name__ == "__main__":
    main()
