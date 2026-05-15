"""Shared pytest fixtures for all test modules."""
import pytest


@pytest.fixture
def sample_application():
    return {
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


@pytest.fixture
def sample_profile():
    return {
        "income_stability_score": 85.0,
        "employment_risk": "Low",
        "credit_history_summary": {"grade": "B", "description": "Good credit", "credit_score": 720},
        "completeness_flags": {"complete": True, "missing_fields": [], "invalid_fields": []},
    }


@pytest.fixture
def sample_risk():
    return {
        "dti_ratio": 0.28,
        "credit_score_risk": "Medium",
        "loan_amount_risk": "Medium",
        "anomalies": [],
        "reasoning": "Moderate financial risk.",
    }


@pytest.fixture
def sample_decision():
    return {
        "classification": "Approve",
        "risk_score": 28.0,
        "confidence_level": "High",
        "key_factors": ["Stable income", "Good credit score", "Manageable DTI"],
        "explanation": "Application approved based on strong financial profile.",
    }


@pytest.fixture
def sample_compliance():
    return {
        "action_taken": "Decision logged and notification prepared",
        "notification_sent": True,
        "case_id": "LOAN-ABCD1234",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "summary": "Congratulations! Loan application LOAN-ABCD1234 for applicant APP-001 has been APPROVED.",
    }
