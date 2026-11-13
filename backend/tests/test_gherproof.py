from app.api import gherproof as routes
from app.services import gherproof_service as service


def test_gherproof_status_is_explicit_about_unprocessed_data():
    body = routes.get_status()
    assert body["processed_event_observations"] == 0
    assert body["local_flood_inference"] == "not_available"
    assert body["event_status"] == "reported_by_news_sources_not_independently_verified"


def test_catalogue_is_query_manifest_not_prediction():
    body = routes.get_catalogue()
    assert body["bbox_status"].startswith("provisional")
    assert all(item["collection"] in {"sentinel-1-grd", "sentinel-2-l2a"} for item in body["items"])


def test_evidence_report_has_no_fabricated_area_or_model_metrics():
    response = routes.get_evidence_report()
    body = service.evidence_report()
    assert body["predicted_spillover_mask"] is None
    assert body["affected_area_estimate"] is None
    assert body["model_evaluation"] is None
    assert "attachment" in response.headers["content-disposition"]
