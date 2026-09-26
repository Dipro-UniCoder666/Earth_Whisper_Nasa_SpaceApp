#!/usr/bin/env python3
"""Step 12B - static validation of the backend foundation and data contract.

Runs with the Python standard library only, so it works even when FastAPI is not
installed. It validates the generated data contract against the verified source
CSVs, checks the scientific-safety constraints, and statically inspects the new
backend modules (AST) for the required routes and forbidden identifiers.
"""

import ast
import csv
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO_ROOT, "data")
CONTRACT = os.path.join(DATA, "step12_backend", "earth_whisper_candidates.json")
STEP6 = os.path.join(DATA, "step6_feature_engine")
STEP10_CSV = os.path.join(DATA, "step10_ai_investigator", "step10_candidate_investigations.csv")
CASE_JSON = os.path.join(DATA, "step11_event_case_file", "earth_event_case_file.json")
CASE_PDF = os.path.join(DATA, "step11_event_case_file", "earth_event_case_file.pdf")
BACKEND = os.path.join(REPO_ROOT, "backend", "app")

FORBIDDEN = [
    "event_probability",
    "erosion_probability",
    "physical_event_probability",
    "confidence_percentage",
    "confirmed_event",
    "erosion_confirmed",
    "landslide_confirmed",
    "ai_confidence_score",
]

results = []


def check(name, ok, detail=""):
    results.append((bool(ok), name, detail))


def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main():
    if not os.path.exists(CONTRACT):
        print("MISSING CONTRACT: " + CONTRACT)
        print("Run: python scripts/step12_build_data_contract.py")
        return 2

    contract = json.load(open(CONTRACT, encoding="utf-8"))
    candidates = contract["candidates"]
    keys = [c["candidate_key"] for c in candidates]
    step10 = {r["candidate_key"]: r for r in load_csv(STEP10_CSV)}
    step8c = {r["candidate_key"]: r for r in load_csv(os.path.join(STEP6, "step8c_evidence_matrix.csv"))}
    step8e = {r["candidate_key"]: r for r in load_csv(os.path.join(STEP6, "step8e_uncertainty_annotations.csv"))}
    step8f = {r["candidate_key"]: r for r in load_csv(os.path.join(STEP6, "step8f_cross_radar_consistency.csv"))}

    check("1. data contract contains 211 candidates", len(candidates) == 211, "count=%d" % len(candidates))
    check("2. candidate_key is unique", len(set(keys)) == len(keys), "unique=%d" % len(set(keys)))
    investigated = [c for c in candidates if c["investigated"]]
    check("3. exactly 32 candidates have investigated=true", len(investigated) == 32, "count=%d" % len(investigated))
    check("3b. investigated set equals the Step 10 CSV",
          set(c["candidate_key"] for c in investigated) == set(step10),
          "matches=%s" % (set(c["candidate_key"] for c in investigated) == set(step10)))
    hh = sum(1 for c in candidates if c["comparison"] == "HH_023_to_029")
    vv = sum(1 for c in candidates if c["comparison"] == "VV_025_to_026")
    check("4. HH count = 195", hh == 195, "count=%d" % hh)
    check("5. VV count = 16", vv == 16, "count=%d" % vv)
    identity_ok = all(c["candidate_key"] == c["comparison"] + "_" + str(c["region_id"]) for c in candidates)
    unique_regions = len(set(c["region_id"] for c in candidates))
    check("6. no candidate uses region_id alone as identity",
          identity_ok and unique_regions < len(candidates),
          "identity_ok=%s, unique_region_ids=%d of %d records" % (identity_ok, unique_regions, len(candidates)))

    evidence_pairs = [("nisar_change", "nisar_change"), ("nisar_change_strength", "nisar_change_strength"),
                      ("nisar_signal_percentile", "nisar_signal_percentile"), ("nisar_signal_band", "nisar_signal_band")]
    mismatches = 0
    for c in candidates:
        src = step8f[c["candidate_key"]]
        for field, src_field in evidence_pairs:
            got = c["nisar"][field]
            want = src[src_field]
            if isinstance(got, (int, float)):
                if abs(float(got) - float(want)) > 1e-12:
                    mismatches += 1
            elif str(got) != str(want):
                mismatches += 1
        if abs(float(c["lon"]) - float(src["lon"])) > 1e-9 or abs(float(c["lat"]) - float(src["lat"])) > 1e-9:
            mismatches += 1
    check("7. Step 8 evidence fields preserved", mismatches == 0, "mismatches=%d" % mismatches)

    unc_mismatch = 0
    for c in candidates:
        src = step8e[c["candidate_key"]]
        if c["uncertainty"]["anomaly_stability_band"] != src["anomaly_stability_band"]:
            unc_mismatch += 1
        if c["uncertainty"]["evidence_limitation"] != src["evidence_limitation"]:
            unc_mismatch += 1
        if int(c["uncertainty"]["comparison_population_size"]) != int(src["comparison_population_size"]):
            unc_mismatch += 1
    check("8. Step 8 uncertainty fields preserved", unc_mismatch == 0, "mismatches=%d" % unc_mismatch)

    cross_mismatch = sum(1 for c in candidates
                         if c["cross_radar"]["cross_radar_status"] != step8f[c["candidate_key"]]["cross_radar_status"])
    check("9. Step 8 cross-radar fields preserved", cross_mismatch == 0, "mismatches=%d" % cross_mismatch)

    case_ok = os.path.exists(CASE_JSON)
    case_cases = 0
    if case_ok:
        case_doc = json.load(open(CASE_JSON, encoding="utf-8"))
        case_cases = len(case_doc.get("cases", []))
    check("10. Step 11 case-file JSON is accessible", case_ok and case_cases == 32,
          "exists=%s, cases=%d" % (case_ok, case_cases))

    pdf_ok = os.path.exists(CASE_PDF)
    pdf_magic = ""
    if pdf_ok:
        with open(CASE_PDF, "rb") as fh:
            pdf_magic = fh.read(5).decode("latin-1")
    check("11. PDF path exists and is a PDF", pdf_ok and pdf_magic.startswith("%PDF"),
          "exists=%s, magic=%s" % (pdf_ok, pdf_magic))

    blob = json.dumps(contract).lower()
    schema_blob = ""
    for base, _dirs, names in os.walk(BACKEND):
        for name in names:
            if name.endswith(".py"):
                schema_blob += open(os.path.join(base, name), encoding="utf-8").read().lower()
    offenders = [word for word in FORBIDDEN if word in blob or word in schema_blob]
    check("12. no event probability / confirmed event field exists", not offenders,
          "offenders=%s" % (offenders if offenders else "none"))
    check("13. no fabricated confidence field exists",
          "confidence_percentage" not in blob and "ai_confidence_score" not in blob,
          "checked contract and backend modules")

    not_tested = sum(1 for c in candidates if c["optical"]["optical_status"] == "not_tested")
    inconclusive = sum(1 for c in candidates
                       if c["optical"]["optical_status"] == "tested_but_inconclusive_no_valid_pixels")
    check("14. optical not_tested preserved", not_tested == 205, "count=%d" % not_tested)
    check("15. tested_but_inconclusive_no_valid_pixels preserved", inconclusive == 6, "count=%d" % inconclusive)

    rainfall_ok = all(c["environmental"]["rainfall_role"] == "environmental_context_only"
                      and c["environmental"]["rainfall_context_status"] == "partial_missing_GUNW_023_14day"
                      for c in candidates)
    gunw023_null = all(c["environmental"]["gunw_023_rainfall_14day_mm"] is None for c in candidates)
    check("16. rainfall remains context-only and GUNW_023 14-day rainfall stays unavailable",
          rainfall_ok and gunw023_null,
          "context_only=%s, gunw023_null=%s" % (rainfall_ok, gunw023_null))
    check("17. exact investigation period is preserved",
          contract.get("investigation_period") == "June–September 2026",
          "period=%r" % contract.get("investigation_period"))
    source_fields_ok = all(
        set(c.get("source_records", {}).get("step8c_evidence_matrix", {})) == set(step8c[c["candidate_key"]])
        and set(c.get("source_records", {}).get("step8e_uncertainty_annotations", {})) == set(step8e[c["candidate_key"]])
        and set(c.get("source_records", {}).get("step8f_cross_radar_consistency", {})) == set(step8f[c["candidate_key"]])
        for c in candidates
    )
    check("18. complete verified source rows are preserved", source_fields_ok)
    required_top_level = {
        "candidate_key", "comparison", "region_id", "lon", "lat", "area_m2",
        "nisar_change", "nisar_change_strength", "nisar_signal_percentile", "nisar_signal_band",
        "s1_median_db", "s1_min_db", "s1_max_db", "s1_pct_le_minus3db",
        "s1_anomaly_percentile", "s1_anomaly_stability", "cross_radar_status", "optical_status",
        "rainfall_context_status", "comparison_population_size", "anomaly_stability_band",
        "evidence_limitation", "observation_summary", "inference_summary", "limitation_summary",
    }
    check("19. required candidate fields are directly available", all(required_top_level <= set(c) for c in candidates))

    # ---- static API-surface inspection (AST, no imports) ----------------
    routes = []
    forbidden_in_code = []
    for base, _dirs, names in os.walk(BACKEND):
        for name in sorted(names):
            if not name.endswith(".py"):
                continue
            full = os.path.join(base, name)
            source = open(full, encoding="utf-8").read()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                            if dec.func.attr in ("get", "post", "put", "delete"):
                                path_arg = dec.args[0].value if dec.args and isinstance(dec.args[0], ast.Constant) else ""
                                routes.append((dec.func.attr.upper(), path_arg))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        low = node.value.lower()
                        for word in FORBIDDEN:
                            if word in low and "no " not in low and "not " not in low:
                                forbidden_in_code.append(word)

    expected = [("GET", "/health"), ("GET", ""), ("GET", "/{candidate_key}"),
                ("GET", "/{candidate_key}/evidence"), ("GET", ""), ("GET", "/pdf")]
    found = [r for r in routes]
    check("S1. six route handlers defined in the API layer", len(routes) == 6,
          "routes=%s" % (routes,))
    check("S2. expected route paths present",
          all((method, p) in found for method, p in expected),
          "expected=%s" % (expected,))
    check("S3. no forbidden identifier in backend source", not forbidden_in_code,
          "offenders=%s" % (forbidden_in_code if forbidden_in_code else "none"))
    api_candidates = open(os.path.join(BACKEND, "api", "candidates.py"), encoding="utf-8").read()
    api_casefile = open(os.path.join(BACKEND, "api", "casefile.py"), encoding="utf-8").read()
    check("S4. routers delegate to the service layer",
          "get_candidate_service" in api_candidates and "get_casefile_service" in api_casefile
          and "open(" not in api_candidates and "open(" not in api_casefile,
          "service imports found; no file access inside routers")

    print("=== Step 12B validation ===")
    failed = 0
    for ok, name, detail in results:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" - " + detail) if detail else ""))
        failed += 0 if ok else 1
    print()
    print("%d checks, %d failed" % (len(results), failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
