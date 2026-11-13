"""Create the Phase 9 evidence-linked, explicitly simulated GherProof scenario."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/gherproof"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    registry = load(DATA / "manifests/evidence_registry.json")
    by_id = {r["evidence_id"]: r for r in registry["records"]}
    comp = load(DATA / "manifests/phase8b_weak_reference_comparison.json")
    optical = load(DATA / "manifests/phase8b_weak_reference_manifest.json")
    phase7 = load(DATA / "manifests/phase7_inference_manifest.json")
    s1_dates = sorted({x["date"] for x in phase7["scenes"]})
    s1_records = [r for r in registry["records"] if r.get("evidence_id", "").startswith("s1-rtc-") and r.get("acquisition_date") in s1_dates]
    s2_records = [r for r in registry["records"] if r.get("evidence_category") == "derived_satellite_measurement" and r.get("title", "").startswith("Sentinel-2") and r.get("acquisition_date") in ("2026-01-10", "2026-01-20")]
    prediction_records = [r for r in registry["records"] if r.get("evidence_category") == "model_prediction" and r.get("evidence_id", "").startswith("prediction-") and r.get("evidence_id", "").endswith("-probability")]
    phase8b_records = [r for r in registry["records"] if r.get("evidence_id", "").startswith("phase8b-") or r.get("evidence_id", "").startswith("optical-weakref-")]
    source_report = by_id["reported-event-2026-01-14"]
    scene_records = []
    for s in phase7["scenes"]:
        if s["model"] != "scratch":
            continue
        scene_records.append({"acquisition_date": s["date"], "item_id": s["item_id"],
                              "relative_orbit": 12 if s["date"] in ("2026-01-12", "2026-01-24") else 150,
                              "direction": "ascending" if s["date"] in ("2026-01-12", "2026-01-24") else "descending",
                              "observation_evidence_id": f"s1-rtc-{s['date']}",
                              "scratch_probability_evidence_id": f"prediction-scratch-{s['date']}-probability",
                              "pretrained_probability_evidence_id": f"prediction-pretrained-{s['date']}-probability",
                              "probability_files": {m: by_id[f"prediction-{m}-{s['date']}-probability"]["derived_file"]["path"] for m in ("scratch", "pretrained")}})
    s2_scene_info = []
    for rec in optical["scenes"]:
        date = rec["date"]
        s2_scene_info.append({"date": date, "datetime_utc": rec["acquisition_datetime_utc"], "item_id": rec["item_id"],
                              "weak_reference_evidence_id": f"optical-weakref-{date}-weak_reference",
                              "ndwi_evidence_id": f"optical-weakref-{date}-ndwi_20m",
                              "mndwi_evidence_id": f"optical-weakref-{date}-mndwi_20m",
                              "scl_evidence_id": f"optical-weakref-{date}-scl_class",
                              "weak_reference_counts": rec["counts"]})
    steps = [
        {"step": 1, "name": "Open investigation", "simulated_user_action": "Select the January 2026 Regional Flood Screening Investigation card.",
         "expected_system_response": "Show a labeled demonstration case, source-reported incident date, and provisional-region banner.", "evidence_ids": ["reported-event-2026-01-14", "geography-provisional-regional-aoi"]},
        {"step": 2, "name": "Incident context", "simulated_user_action": "Expand reported context and source links.",
         "expected_system_response": "Present attributed reports and reported place names; clearly show that reported claims and date are not independently verified.",
         "evidence_ids": ["reported-event-2026-01-14"], "source_refs": source_report["source_provenance"]},
        {"step": 3, "name": "Satellite review", "simulated_user_action": "Select a Sentinel-1 acquisition and inspect its date, orbit, direction, observation footprint and provenance.",
         "expected_system_response": "Show each acquisition as its own scene; keep ascending relative orbit 12 and descending relative orbit 150 separate.",
         "evidence_ids": [x["observation_evidence_id"] for x in scene_records]},
        {"step": 4, "name": "Optical comparison", "simulated_user_action": "Toggle January 10/20 optical weak-reference, NDWI, MNDWI, SCL and uncertainty layers.",
         "expected_system_response": "Display the fixed optical-only thresholds, 20 m comparison grid, clear/invalid masks and exact acquisition timestamps; do not call candidates confirmed water.",
         "evidence_ids": [x["weak_reference_evidence_id"] for x in s2_scene_info] + [x["ndwi_evidence_id"] for x in s2_scene_info] + [x["mndwi_evidence_id"] for x in s2_scene_info]},
        {"step": 5, "name": "AI screening", "simulated_user_action": "Toggle scratch and pretrained outputs independently for one acquisition.",
         "expected_system_response": "Show separate exploratory prediction layers and preserve model selection as none.",
         "evidence_ids": [x[f"{m}_probability_evidence_id"] for x in scene_records for m in ("scratch", "pretrained")]},
        {"step": 6, "name": "Uncertainty review", "simulated_user_action": "Open optical/SAR agreement, model disagreement and joint coverage views.",
         "expected_system_response": "Keep agreements, disagreements, optical uncertainty and unavailable coverage distinct; report temporal offsets and block variation.",
         "evidence_ids": [r["evidence_id"] for r in phase8b_records if "agreement" in r["evidence_id"] or "disagreement" in r["evidence_id"] or "coverage" in r["evidence_id"]]},
        {"step": 7, "name": "Evidence assessment", "simulated_user_action": "Open the evidence panel and filter by observations, derived measurements, weak references, predictions and provisional context.",
         "expected_system_response": "Show category, status, file checksum, processing provenance and limitations. Weak-reference metrics must not be labeled local accuracy.",
         "evidence_ids": ["reported-event-2026-01-14", "geography-provisional-regional-aoi"] + [x["weak_reference_evidence_id"] for x in s2_scene_info]},
        {"step": 8, "name": "Investigation report", "simulated_user_action": "Generate a screening summary for review.",
         "expected_system_response": "Summarize per-model/per-acquisition weak-reference consistency and state required follow-up: field observations, human labels, verified site geometry and authoritative event records. No impact estimate or breach diagnosis is produced.",
         "evidence_ids": ["reported-event-2026-01-14"] + [r["evidence_id"] for r in phase8b_records if r.get("evidence_category") == "model_comparison"]},
    ]
    scenario = {
        "scenario_id": "january_2026_regional_screening_demo",
        "scenario_title": "January 2026 — Regional Flood Screening Investigation",
        "demonstration_mode": "simulated_workflow_using_real_saved_evidence",
        "is_simulated": True,
        "user_persona": {"role": "hypothetical regional disaster-monitoring officer", "description": "A fictional user reviewing a reported embankment-failure incident in the Manirampur/Abhaynagar region; no real officer or agency use is claimed."},
        "investigation_dates": {"reported_event_date": "2026-01-14", "date_status": "reported/inferred; not independently verified", "analysis_period": ["2026-01-09", "2026-01-24"]},
        "incident_context": {"status": "source_reported_unverified", "reported_location_descriptions": ["Sujatpur Pallimangal Fisheries Enclosure", "Sujatpur mouza / Beel Kedaria / Bhavadah context as described in secondary reports", "southern embankment and adjacent khal as reported; not spatially located"],
                             "reported_affected_village_names": ["Sujatpur", "Hatgachha", "Kultia", "Moshiahati", "Bedbhita", "Balarabad"],
                             "village_names_attribution": "Reported in the linked January 16 Dhaka Post account; not verified by this evidence pipeline.",
                             "reported_claims": [{"source": "Daily Country Today", "claim": "Headline reports 1,500 bighas flooded and over 500 families homeless in Jashore.", "status": "attributed news claim; not a satellite measurement", "url": "https://dailycountrytodaybd.com/bn/story/1%2C500-bighas-of-land-flooded-as-embankment-collapses%2C-over-500-families-homeless-in-jashore"},
                                               {"source": "Dhaka Post", "claim": "Reports the Pallimangal enclosure incident and names six affected-village locations.", "status": "attributed news claim; not independently verified", "url": "https://www.dhakapost.com/country/424238"},
                                               {"source": "Samakal", "claim": "Places the reported operation in Sujatpur mouza / Beel Kedaria and describes a southern embankment beside a khal.", "status": "textual reported context; no geodetic point or boundary", "url": "https://samakal.com/whole-country/article/334020"}],
                             "coordinates": None, "verified_enclosure_boundary": False},
        "available_satellite_scenes": scene_records,
        "available_optical_indicators": s2_scene_info,
        "available_model_predictions": [{"model": m, "readiness": "exploratory_only", "prediction_evidence_ids": [x[f"{m}_probability_evidence_id"] for x in scene_records]} for m in ("scratch", "pretrained")],
        "weak_reference_comparison_manifest": "data/gherproof/manifests/phase8b_weak_reference_comparison.json",
        "weak_reference_comparison_summary": [{k: r.get(k) for k in ("model", "sentinel1_date", "sentinel1_relative_orbit", "sentinel1_direction", "sentinel2_date", "date_offset_hours", "common_valid_comparison_pixels", "weak_reference_agreement", "weak_reference_positive_agreement", "weak_reference_negative_agreement")} for r in comp["per_model_acquisition_results"]],
        "evidence_registry_references": ["data/gherproof/manifests/evidence_registry.json", "reported-event-2026-01-14", "geography-provisional-regional-aoi"],
        "demonstration_steps": steps,
        "simulated_user_actions": [x["simulated_user_action"] for x in steps],
        "scientific_limitations": ["All optical reference states are automated weak references, not human or field ground truth.", "Model metrics are weak_reference_agreement, not local model accuracy.", "Sentinel-1/2 acquisitions are not simultaneous; each exact timestamp offset is displayed.", "Sentinel-1 orbit directions and relative orbits remain separate; no geometry pooling.", "No official village boundary, exact Pallimangal boundary or breach coordinate is available.", "No confirmed flood extent, cropland area, fish loss, financial loss or affected-family estimate is produced.", "No incident causality or embankment failure is inferred from spatial adjacency."],
        "readiness_statuses": {"model_readiness": "exploratory_only", "human_reference_labels": "human_review_pending", "impact_quantification": "not_approved", "pallimangal_location": "unresolved", "demonstration_scenario": "ready_for_phase9_frontend_workflow_prototyping"},
        "phase9_api_paths": ["GET /api/gherproof/scenarios/january_2026_regional_screening_demo", "GET /api/gherproof/weak-reference", "GET /api/gherproof/comparisons", "GET /api/gherproof/evidence", "GET /api/gherproof/scenes", "GET /api/gherproof/predictions", "GET /api/gherproof/layers", "GET /api/gherproof/reports/summary"],
        "source_event_registry_record": {"evidence_id": source_report["evidence_id"], "status": source_report["confidence_or_validation_status"], "source_provenance": source_report["source_provenance"]},
    }
    out = DATA / "scenarios/january_2026_regional_screening_demo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scenario, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": out.relative_to(ROOT).as_posix(), "steps": len(steps), "s1_scenes": len(scene_records), "s2_scenes": len(s2_scene_info), "predictions": len(prediction_records), "registered_phase8b_layers": len(phase8b_records)}, indent=2))


if __name__ == "__main__":
    main()
