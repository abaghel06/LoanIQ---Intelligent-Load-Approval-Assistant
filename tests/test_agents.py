"""Tests for MCP server tools, agent classes, and API health endpoint."""
import json
import sys
import os
from unittest.mock import patch, AsyncMock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── MCP tool unit tests (import server modules directly) ──────────────────────

class TestApplicantDBTools:
    def setup_method(self):
        from mcp_servers.applicant_db_server import (
            get_income_stability_score,
            get_employment_risk,
            get_credit_history_summary,
            check_application_completeness,
        )
        self.income_score = get_income_stability_score
        self.emp_risk = get_employment_risk
        self.credit_summary = get_credit_history_summary
        self.completeness = check_application_completeness

    def test_income_stability_salaried_high_income(self):
        score = self.income_score(120000, "Salaried")
        assert score == 100.0

    def test_income_stability_unemployed(self):
        score = self.income_score(0, "Unemployed")
        assert score <= 10.0

    def test_employment_risk_salaried(self):
        assert self.emp_risk("Salaried") == "Low"

    def test_employment_risk_unemployed(self):
        assert self.emp_risk("Unemployed") == "High"

    def test_credit_history_excellent(self):
        result = json.loads(self.credit_summary(820))
        assert result["grade"] == "A+"

    def test_credit_history_poor(self):
        result = json.loads(self.credit_summary(450))
        assert result["grade"] in ("D", "F")

    def test_completeness_valid_application(self):
        data = {
            "applicant_id": "A1", "age": 30, "income": 50000,
            "employment_type": "Salaried", "credit_score": 700,
            "loan_amount": 100000, "tenure_months": 60,
            "existing_liabilities": 5000, "location": "NYC",
            "application_timestamp": "2026-01-01T00:00:00Z",
        }
        result = json.loads(self.completeness(json.dumps(data)))
        assert result["complete"] is True

    def test_completeness_missing_field(self):
        data = {"applicant_id": "A1", "age": 30}
        result = json.loads(self.completeness(json.dumps(data)))
        assert result["complete"] is False
        assert len(result["missing_fields"]) > 0


class TestRiskRulesTools:
    def setup_method(self):
        from mcp_servers.risk_rules_server import (
            calculate_dti_ratio,
            assess_credit_score_risk,
            assess_loan_amount_risk,
            detect_anomalies,
        )
        self.dti = calculate_dti_ratio
        self.credit_risk = assess_credit_score_risk
        self.loan_risk = assess_loan_amount_risk
        self.anomalies = detect_anomalies

    def test_dti_reasonable(self):
        dti = self.dti(income=60000, loan_amount=100000, existing_liabilities=5000, tenure_months=60)
        assert 0 < dti < 1

    def test_dti_zero_income(self):
        dti = self.dti(income=0, loan_amount=50000, existing_liabilities=0, tenure_months=12)
        assert dti == 999.0

    def test_credit_risk_excellent(self):
        assert self.credit_risk(800) == "Low"

    def test_credit_risk_poor(self):
        assert self.credit_risk(450) == "Very High"

    def test_loan_risk_low(self):
        assert self.loan_risk(50000, 100000) == "Low"

    def test_loan_risk_very_high(self):
        assert self.loan_risk(500000, 50000) == "Very High"

    def test_no_anomalies_normal_application(self):
        data = {
            "age": 35, "income": 80000, "credit_score": 720,
            "loan_amount": 100000, "existing_liabilities": 5000,
            "employment_type": "Salaried", "tenure_months": 60,
        }
        result = json.loads(self.anomalies(json.dumps(data)))
        assert isinstance(result, list)

    def test_anomaly_unemployed_large_loan(self):
        data = {
            "age": 30, "income": 0, "credit_score": 500,
            "loan_amount": 500000, "existing_liabilities": 0,
            "employment_type": "Unemployed", "tenure_months": 60,
        }
        result = json.loads(self.anomalies(json.dumps(data)))
        assert len(result) > 0


class TestDecisionSynthesisTools:
    def setup_method(self):
        from mcp_servers.decision_synthesis_server import (
            calculate_risk_score,
            determine_classification,
            get_confidence_level,
        )
        self.risk_score = calculate_risk_score
        self.classify = determine_classification
        self.confidence = get_confidence_level

    def test_risk_score_low_risk(self):
        profile = {"income_stability_score": 85, "employment_risk": "Low", "completeness_flags": {"complete": True}}
        risk = {"dti_ratio": 0.25, "credit_score_risk": "Low", "loan_amount_risk": "Low", "anomalies": []}
        score = self.risk_score(json.dumps(profile), json.dumps(risk))
        assert score < 50

    def test_risk_score_high_risk(self):
        profile = {"income_stability_score": 20, "employment_risk": "High", "completeness_flags": {"complete": False}}
        risk = {"dti_ratio": 0.8, "credit_score_risk": "Very High", "loan_amount_risk": "Very High", "anomalies": ["flag1", "flag2"]}
        score = self.risk_score(json.dumps(profile), json.dumps(risk))
        assert score > 60

    def test_classify_approve(self):
        assert self.classify(20.0, False, True) == "Approve"

    def test_classify_reject(self):
        assert self.classify(80.0, True, True) == "Reject"

    def test_confidence_high(self):
        assert self.confidence(10.0) == "High"
        assert self.confidence(90.0) == "High"

    def test_confidence_low(self):
        assert self.confidence(50.0) == "Low"


class TestNotificationTools:
    def setup_method(self):
        from mcp_servers.notification_server import (
            generate_case_id,
            format_notification_summary,
        )
        self.gen_case_id = generate_case_id
        self.notify = format_notification_summary

    def test_case_id_format(self):
        case_id = self.gen_case_id("APP-001", "2026-01-01T00:00:00Z")
        assert case_id.startswith("LOAN-")
        assert len(case_id) == 13  # "LOAN-" + 8 chars

    def test_case_id_deterministic(self):
        id1 = self.gen_case_id("APP-001", "2026-01-01T00:00:00Z")
        id2 = self.gen_case_id("APP-001", "2026-01-01T00:00:00Z")
        assert id1 == id2

    def test_notification_approve(self):
        msg = self.notify("Approve", "APP-001", "LOAN-ABC12345")
        assert "APPROVED" in msg

    def test_notification_reject(self):
        msg = self.notify("Reject", "APP-001", "LOAN-ABC12345")
        assert "REJECTED" in msg

    def test_notification_review(self):
        msg = self.notify("Manual Review", "APP-001", "LOAN-ABC12345")
        assert "MANUAL REVIEW" in msg


# ── Applicant DB edge cases ────────────────────────────────────────────────────

class TestApplicantDBEdgeCases:
    def setup_method(self):
        from mcp_servers.applicant_db_server import (
            get_income_stability_score,
            get_employment_risk,
            get_credit_history_summary,
            check_application_completeness,
        )
        self.income_score = get_income_stability_score
        self.emp_risk = get_employment_risk
        self.credit_summary = get_credit_history_summary
        self.completeness = check_application_completeness

    def test_income_stability_all_employment_types(self):
        assert self.income_score(30000, "Salaried") == 80.0
        assert self.income_score(30000, "Self-Employed") == 60.0
        assert self.income_score(30000, "Contract") == 50.0
        assert self.income_score(30000, "Unemployed") == 10.0  # base=10, income_bonus=0

    def test_income_stability_all_income_tiers(self):
        # Salaried base=80
        assert self.income_score(100000, "Salaried") == 100.0   # 80+20
        assert self.income_score(60000, "Salaried") == 90.0    # 80+10
        assert self.income_score(30000, "Salaried") == 80.0    # 80+0
        assert self.income_score(15000, "Salaried") == 70.0    # 80-10
        assert self.income_score(1000, "Salaried") == 60.0     # 80-20

    def test_income_stability_unknown_employment(self):
        score = self.income_score(60000, "Freelancer")
        assert score == 50.0  # base=40, +10

    def test_income_stability_clamped_to_zero(self):
        assert self.income_score(0, "Unemployed") == 0.0  # 10-20=-10 → clamp to 0

    def test_employment_risk_all_types(self):
        assert self.emp_risk("Salaried") == "Low"
        assert self.emp_risk("Self-Employed") == "Medium"
        assert self.emp_risk("Contract") == "Medium"
        assert self.emp_risk("Unemployed") == "High"

    def test_employment_risk_unknown_type(self):
        assert self.emp_risk("Freelancer") == "Medium"

    def test_credit_history_all_grades(self):
        assert json.loads(self.credit_summary(820))["grade"] == "A+"
        assert json.loads(self.credit_summary(800))["grade"] == "A+"
        assert json.loads(self.credit_summary(740))["grade"] == "A"
        assert json.loads(self.credit_summary(739))["grade"] == "B"
        assert json.loads(self.credit_summary(670))["grade"] == "B"
        assert json.loads(self.credit_summary(669))["grade"] == "C"
        assert json.loads(self.credit_summary(580))["grade"] == "C"
        assert json.loads(self.credit_summary(579))["grade"] == "D"
        assert json.loads(self.credit_summary(500))["grade"] == "D"
        assert json.loads(self.credit_summary(499))["grade"] == "F"

    def test_credit_history_includes_score(self):
        result = json.loads(self.credit_summary(720))
        assert result["credit_score"] == 720

    def test_completeness_invalid_age(self):
        data = {
            "applicant_id": "A1", "age": 17, "income": 50000,
            "employment_type": "Salaried", "credit_score": 700,
            "loan_amount": 100000, "tenure_months": 60,
            "existing_liabilities": 5000, "location": "Mumbai",
            "application_timestamp": "2026-01-01T00:00:00Z",
        }
        result = json.loads(self.completeness(json.dumps(data)))
        assert result["complete"] is False
        assert any("age" in f for f in result["invalid_fields"])

    def test_completeness_invalid_credit_score(self):
        data = {
            "applicant_id": "A1", "age": 30, "income": 50000,
            "employment_type": "Salaried", "credit_score": 200,
            "loan_amount": 100000, "tenure_months": 60,
            "existing_liabilities": 5000, "location": "Mumbai",
            "application_timestamp": "2026-01-01T00:00:00Z",
        }
        result = json.loads(self.completeness(json.dumps(data)))
        assert result["complete"] is False
        assert any("credit_score" in f for f in result["invalid_fields"])

    def test_completeness_invalid_json(self):
        result = json.loads(self.completeness("not json"))
        assert result["complete"] is False


# ── Risk rules edge cases ──────────────────────────────────────────────────────

class TestRiskRulesEdgeCases:
    def setup_method(self):
        from mcp_servers.risk_rules_server import (
            calculate_dti_ratio,
            assess_credit_score_risk,
            assess_loan_amount_risk,
            detect_anomalies,
        )
        self.dti = calculate_dti_ratio
        self.credit_risk = assess_credit_score_risk
        self.loan_risk = assess_loan_amount_risk
        self.anomalies = detect_anomalies

    def test_dti_formula_accuracy(self):
        # income=12000, loan=120000, liabilities=12000, tenure=120
        # monthly_income=1000, monthly_loan=1000, monthly_liab=1000 → dti=2.0
        dti = self.dti(income=12000, loan_amount=120000, existing_liabilities=12000, tenure_months=120)
        assert dti == 2.0

    def test_credit_risk_all_tiers(self):
        assert self.credit_risk(740) == "Low"
        assert self.credit_risk(739) == "Medium"
        assert self.credit_risk(670) == "Medium"
        assert self.credit_risk(669) == "High"
        assert self.credit_risk(580) == "High"
        assert self.credit_risk(579) == "Very High"
        assert self.credit_risk(300) == "Very High"

    def test_loan_risk_all_tiers(self):
        # ratio = loan/income
        assert self.loan_risk(200000, 100000) == "Low"     # ratio=2
        assert self.loan_risk(200001, 100000) == "Medium"  # ratio>2
        assert self.loan_risk(400000, 100000) == "Medium"  # ratio=4
        assert self.loan_risk(400001, 100000) == "High"    # ratio>4
        assert self.loan_risk(600000, 100000) == "High"    # ratio=6
        assert self.loan_risk(600001, 100000) == "Very High"

    def test_loan_risk_zero_income(self):
        assert self.loan_risk(100000, 0) == "Very High"

    def test_anomaly_very_young_large_loan(self):
        data = {"age": 20, "income": 50000, "credit_score": 600,
                "loan_amount": 60000, "existing_liabilities": 0,
                "employment_type": "Salaried", "tenure_months": 60}
        result = json.loads(self.anomalies(json.dumps(data)))
        assert any("young" in a.lower() for a in result)

    def test_anomaly_near_retirement_long_tenure(self):
        data = {"age": 70, "income": 50000, "credit_score": 700,
                "loan_amount": 10000, "existing_liabilities": 0,
                "employment_type": "Salaried", "tenure_months": 180}
        result = json.loads(self.anomalies(json.dumps(data)))
        assert any("retirement" in a.lower() for a in result)

    def test_anomaly_poor_credit_large_loan(self):
        data = {"age": 35, "income": 80000, "credit_score": 400,
                "loan_amount": 60000, "existing_liabilities": 0,
                "employment_type": "Salaried", "tenure_months": 60}
        result = json.loads(self.anomalies(json.dumps(data)))
        assert any("credit" in a.lower() for a in result)

    def test_anomaly_high_liabilities_ratio(self):
        data = {"age": 35, "income": 10000, "credit_score": 700,
                "loan_amount": 10000, "existing_liabilities": 9000,
                "employment_type": "Salaried", "tenure_months": 60}
        result = json.loads(self.anomalies(json.dumps(data)))
        assert any("liabilit" in a.lower() for a in result)

    def test_anomaly_zero_income_non_unemployed(self):
        data = {"age": 35, "income": 0, "credit_score": 700,
                "loan_amount": 10000, "existing_liabilities": 0,
                "employment_type": "Salaried", "tenure_months": 60}
        result = json.loads(self.anomalies(json.dumps(data)))
        assert any("zero income" in a.lower() for a in result)

    def test_anomaly_invalid_json(self):
        result = json.loads(self.anomalies("bad json"))
        assert result == ["invalid JSON input"]


# ── Decision synthesis edge cases ─────────────────────────────────────────────

class TestDecisionSynthesisEdgeCases:
    def setup_method(self):
        from mcp_servers.decision_synthesis_server import (
            calculate_risk_score,
            determine_classification,
            get_confidence_level,
        )
        self.risk_score = calculate_risk_score
        self.classify = determine_classification
        self.confidence = get_confidence_level

    def test_classify_incomplete_app_is_manual_review(self):
        assert self.classify(20.0, False, False) == "Manual Review"

    def test_classify_mid_range_with_anomalies_is_review(self):
        assert self.classify(50.0, True, True) == "Manual Review"

    def test_classify_mid_range_no_anomalies_below_50_is_approve(self):
        assert self.classify(45.0, False, True) == "Approve"
        assert self.classify(50.0, False, True) == "Approve"

    def test_classify_mid_range_no_anomalies_above_50_is_review(self):
        assert self.classify(50.1, False, True) == "Manual Review"
        assert self.classify(64.9, False, True) == "Manual Review"

    def test_classify_boundary_35_is_approve(self):
        assert self.classify(34.9, False, True) == "Approve"

    def test_classify_boundary_65_is_reject(self):
        assert self.classify(65.0, False, True) == "Reject"
        assert self.classify(65.0, True, True) == "Reject"

    def test_confidence_all_tiers(self):
        assert self.confidence(24.9) == "High"
        assert self.confidence(25.0) == "Medium"
        assert self.confidence(39.9) == "Medium"
        assert self.confidence(40.0) == "Low"
        assert self.confidence(65.0) == "Low"
        assert self.confidence(65.1) == "Medium"
        assert self.confidence(80.0) == "Medium"  # >65 and <=80 → Medium
        assert self.confidence(80.1) == "High"   # >80 → High

    def test_risk_score_invalid_json_returns_75(self):
        score = self.risk_score("not json", "{}")
        assert score == 75.0

    def test_risk_score_clamped_to_100(self):
        profile = {"income_stability_score": 0, "employment_risk": "High",
                   "completeness_flags": {"complete": False}}
        risk = {"dti_ratio": 1.0, "credit_score_risk": "Very High",
                "loan_amount_risk": "Very High", "anomalies": ["a", "b", "c", "d"]}
        score = self.risk_score(json.dumps(profile), json.dumps(risk))
        assert score <= 100.0

    def test_risk_score_clamped_to_zero(self):
        profile = {"income_stability_score": 100, "employment_risk": "Low",
                   "completeness_flags": {"complete": True}}
        risk = {"dti_ratio": 0.1, "credit_score_risk": "Low",
                "loan_amount_risk": "Low", "anomalies": []}
        score = self.risk_score(json.dumps(profile), json.dumps(risk))
        assert score >= 0.0


# ── Log decision to file ───────────────────────────────────────────────────────

class TestLogDecisionToFile:
    def setup_method(self):
        from mcp_servers.notification_server import log_decision_to_file
        self.log_decision = log_decision_to_file

    def test_creates_file_and_logs_record(self, tmp_path):
        log_file = str(tmp_path / "test_log.json")
        with patch("mcp_servers.notification_server.DATA_DIR", str(tmp_path)), \
             patch("mcp_servers.notification_server.LOG_FILE", log_file):
            result = json.loads(
                self.log_decision("LOAN-TEST01", "APP-001", '{"classification": "Approve"}')
            )

        assert result["status"] == "logged"
        assert result["case_id"] == "LOAN-TEST01"
        records = json.loads((tmp_path / "test_log.json").read_text())
        assert len(records) == 1
        assert records[0]["case_id"] == "LOAN-TEST01"
        assert records[0]["applicant_id"] == "APP-001"

    def test_appends_to_existing_file(self, tmp_path):
        log_file = str(tmp_path / "log.json")
        with patch("mcp_servers.notification_server.DATA_DIR", str(tmp_path)), \
             patch("mcp_servers.notification_server.LOG_FILE", log_file):
            self.log_decision("LOAN-001", "APP-001", '{"classification": "Approve"}')
            self.log_decision("LOAN-002", "APP-002", '{"classification": "Reject"}')

        records = json.loads((tmp_path / "log.json").read_text())
        assert len(records) == 2
        assert records[1]["case_id"] == "LOAN-002"

    def test_handles_corrupt_existing_file(self, tmp_path):
        log_file = tmp_path / "log.json"
        log_file.write_text("not valid json")

        with patch("mcp_servers.notification_server.DATA_DIR", str(tmp_path)), \
             patch("mcp_servers.notification_server.LOG_FILE", str(log_file)):
            result = json.loads(
                self.log_decision("LOAN-003", "APP-003", '{"classification": "Reject"}')
            )

        assert result["status"] == "logged"
        records = json.loads(log_file.read_text())
        assert len(records) == 1


# ── MCP tool helper ────────────────────────────────────────────────────────────

class TestMCPToolHelper:
    def test_converts_tool_with_schema(self):
        from agents.base import _mcp_tool_to_anthropic

        class MockTool:
            name = "my_tool"
            description = "Does something"
            inputSchema = {"type": "object", "properties": {"x": {"type": "string"}}}

        result = _mcp_tool_to_anthropic(MockTool())
        assert result["name"] == "my_tool"
        assert result["description"] == "Does something"
        assert result["input_schema"]["properties"]["x"]["type"] == "string"

    def test_converts_tool_without_schema(self):
        from agents.base import _mcp_tool_to_anthropic

        class MockTool:
            name = "empty_tool"
            description = None
            inputSchema = None

        result = _mcp_tool_to_anthropic(MockTool())
        assert result["description"] == ""
        assert result["input_schema"] == {"type": "object", "properties": {}}


# ── Agent class tests (BaseAgent.run mocked) ───────────────────────────────────

class TestAgentClasses:
    async def test_applicant_profile_agent_parses_valid_json(self, sample_application):
        from agents.applicant_profile_agent import ApplicantProfileAgent
        from agents.base import BaseAgent

        mock_output = json.dumps({
            "income_stability_score": 90.0,
            "employment_risk": "Low",
            "credit_history_summary": {"grade": "A", "description": "Very good", "credit_score": 750},
            "completeness_flags": {"complete": True, "missing_fields": [], "invalid_fields": []},
        })

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value=mock_output):
            result = await ApplicantProfileAgent().analyze(sample_application)

        assert result["income_stability_score"] == 90.0
        assert result["employment_risk"] == "Low"
        assert result["completeness_flags"]["complete"] is True

    async def test_applicant_profile_agent_fallback_on_bad_json(self, sample_application):
        from agents.applicant_profile_agent import ApplicantProfileAgent
        from agents.base import BaseAgent

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value="not {{json"):
            result = await ApplicantProfileAgent().analyze(sample_application)

        assert result["income_stability_score"] == 50.0
        assert result["employment_risk"] == "Medium"
        assert result["completeness_flags"]["complete"] is False
        assert "raw_response" in result

    async def test_financial_risk_agent_parses_valid_json(self, sample_application):
        from agents.financial_risk_agent import FinancialRiskAgent
        from agents.base import BaseAgent

        mock_output = json.dumps({
            "dti_ratio": 0.32,
            "credit_score_risk": "Medium",
            "loan_amount_risk": "High",
            "anomalies": [],
            "reasoning": "Moderate risk.",
        })

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value=mock_output):
            result = await FinancialRiskAgent().analyze(sample_application)

        assert result["dti_ratio"] == 0.32
        assert result["loan_amount_risk"] == "High"
        assert result["anomalies"] == []

    async def test_financial_risk_agent_fallback_on_bad_json(self, sample_application):
        from agents.financial_risk_agent import FinancialRiskAgent
        from agents.base import BaseAgent

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value="garbage"):
            result = await FinancialRiskAgent().analyze(sample_application)

        assert result["dti_ratio"] == 0.5
        assert result["credit_score_risk"] == "Medium"
        assert "raw_response" in result

    async def test_loan_decision_agent_parses_valid_json(
        self, sample_application, sample_profile, sample_risk
    ):
        from agents.loan_decision_agent import LoanDecisionAgent
        from agents.base import BaseAgent

        mock_output = json.dumps({
            "classification": "Reject",
            "risk_score": 78.0,
            "confidence_level": "High",
            "key_factors": ["High DTI", "Low credit"],
            "explanation": "High risk application rejected.",
        })

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value=mock_output):
            result = await LoanDecisionAgent().decide(
                sample_application, sample_profile, sample_risk
            )

        assert result["classification"] == "Reject"
        assert result["risk_score"] == 78.0
        assert len(result["key_factors"]) == 2

    async def test_loan_decision_agent_fallback(
        self, sample_application, sample_profile, sample_risk
    ):
        from agents.loan_decision_agent import LoanDecisionAgent
        from agents.base import BaseAgent

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value="invalid"):
            result = await LoanDecisionAgent().decide(
                sample_application, sample_profile, sample_risk
            )

        assert result["classification"] == "Manual Review"
        assert result["risk_score"] == 50.0
        assert "raw_response" in result

    async def test_compliance_agent_parses_valid_json(self, sample_application, sample_decision):
        from agents.compliance_agent import ComplianceAgent
        from agents.base import BaseAgent

        mock_output = json.dumps({
            "action_taken": "Decision logged and notification prepared",
            "notification_sent": True,
            "case_id": "LOAN-ABCD1234",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "summary": "Congratulations! Application LOAN-ABCD1234 has been APPROVED.",
        })

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value=mock_output):
            result = await ComplianceAgent().process(sample_application, sample_decision)

        assert result["case_id"] == "LOAN-ABCD1234"
        assert result["notification_sent"] is True

    async def test_compliance_agent_fallback(self, sample_application, sample_decision):
        from agents.compliance_agent import ComplianceAgent
        from agents.base import BaseAgent

        with patch.object(BaseAgent, "run", new_callable=AsyncMock, return_value=""):
            result = await ComplianceAgent().process(sample_application, sample_decision)

        assert result["notification_sent"] is False
        assert result["case_id"] == "LOAN-ERROR"
        assert "failed" in result["action_taken"].lower()


# ── FastAPI integration test ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint():
    import httpx
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            resp = await client.get("/health", timeout=5)
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}
        except httpx.ConnectError:
            pytest.skip("FastAPI server not running — skipping integration test")
