"""Tests for the FastAPI microservice endpoints."""
import sys
import os
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "applicant_id": "APP-001",
    "age": 35,
    "income": 750000.0,
    "employment_type": "Salaried",
    "credit_score": 720,
    "loan_amount": 1500000.0,
    "tenure_months": 60,
    "existing_liabilities": 100000.0,
    "location": "Mumbai",
    "application_timestamp": "2026-01-01T00:00:00Z",
}

MOCK_PIPELINE_STATE = {
    "application": VALID_PAYLOAD,
    "profile_analysis": {},
    "risk_analysis": {},
    "loan_decision": {
        "classification": "Approve",
        "risk_score": 28.0,
        "confidence_level": "High",
        "key_factors": ["Stable income", "Good credit"],
        "explanation": "Strong financial profile.",
    },
    "compliance_result": {
        "action_taken": "Decision logged and notification prepared",
        "notification_sent": True,
        "case_id": "LOAN-ABCD1234",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "summary": "Congratulations! Application approved.",
    },
    "error": None,
}


class TestHealthEndpoint:
    def test_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_returns_ok_status(self):
        resp = client.get("/health")
        assert resp.json() == {"status": "ok"}


class TestEvaluateLoanValidation:
    def test_invalid_age_too_young_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "age": 17})
        assert resp.status_code == 422

    def test_invalid_age_too_old_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "age": 81})
        assert resp.status_code == 422

    def test_boundary_age_18_is_valid(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "age": 18})
        assert resp.status_code == 200

    def test_boundary_age_80_is_valid(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "age": 80})
        assert resp.status_code == 200

    def test_invalid_credit_score_too_low_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "credit_score": 299})
        assert resp.status_code == 422

    def test_invalid_credit_score_too_high_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "credit_score": 851})
        assert resp.status_code == 422

    def test_invalid_income_zero_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "income": 0.0})
        assert resp.status_code == 422

    def test_invalid_loan_amount_zero_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "loan_amount": 0.0})
        assert resp.status_code == 422

    def test_negative_liabilities_returns_422(self):
        resp = client.post("/api/loan/evaluate", json={**VALID_PAYLOAD, "existing_liabilities": -1.0})
        assert resp.status_code == 422

    def test_missing_applicant_id_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "applicant_id"}
        resp = client.post("/api/loan/evaluate", json=payload)
        assert resp.status_code == 422

    def test_missing_income_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "income"}
        resp = client.post("/api/loan/evaluate", json=payload)
        assert resp.status_code == 422


class TestEvaluateLoanResponse:
    def test_valid_payload_returns_200(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_all_response_fields_present(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        data = resp.json()
        for field in ["application_id", "classification", "risk_score", "confidence_level",
                      "key_factors", "explanation", "case_id", "timestamp", "summary"]:
            assert field in data, f"Missing field: {field}"

    def test_response_maps_applicant_id(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["application_id"] == "APP-001"

    def test_response_maps_classification(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["classification"] == "Approve"

    def test_response_maps_risk_score(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["risk_score"] == 28.0

    def test_response_maps_case_id(self):
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["case_id"] == "LOAN-ABCD1234"

    def test_reject_classification_mapped_correctly(self):
        state = {
            **MOCK_PIPELINE_STATE,
            "loan_decision": {**MOCK_PIPELINE_STATE["loan_decision"],
                              "classification": "Reject", "risk_score": 82.0},
        }
        with patch("orchestrator.graph.evaluate_loan", return_value=state):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["classification"] == "Reject"

    def test_manual_review_classification_mapped_correctly(self):
        state = {
            **MOCK_PIPELINE_STATE,
            "loan_decision": {**MOCK_PIPELINE_STATE["loan_decision"],
                              "classification": "Manual Review", "risk_score": 55.0},
        }
        with patch("orchestrator.graph.evaluate_loan", return_value=state):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.json()["classification"] == "Manual Review"

    def test_null_decision_uses_defaults(self):
        state = {**MOCK_PIPELINE_STATE, "loan_decision": None, "compliance_result": None}
        with patch("orchestrator.graph.evaluate_loan", return_value=state):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        data = resp.json()
        assert resp.status_code == 200
        assert data["classification"] == "Manual Review"
        assert data["risk_score"] == 50.0
        assert data["confidence_level"] == "Low"
        assert data["case_id"] == "N/A"

    def test_pipeline_exception_returns_500(self):
        with patch("orchestrator.graph.evaluate_loan", side_effect=RuntimeError("Pipeline failed")):
            resp = client.post("/api/loan/evaluate", json=VALID_PAYLOAD)
        assert resp.status_code == 500
        assert "Pipeline failed" in resp.json()["detail"]

    def test_application_timestamp_auto_populated(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "application_timestamp"}
        with patch("orchestrator.graph.evaluate_loan", return_value=MOCK_PIPELINE_STATE):
            resp = client.post("/api/loan/evaluate", json=payload)
        assert resp.status_code == 200
