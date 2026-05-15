"""Tests for the LangGraph orchestrator — graph nodes and evaluate_loan wrapper."""
import sys
import os
from unittest.mock import patch, AsyncMock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_state(**overrides):
    state = {
        "application": {
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
        },
        "profile_analysis": None,
        "risk_analysis": None,
        "loan_decision": None,
        "compliance_result": None,
        "error": None,
    }
    state.update(overrides)
    return state


class TestBuildGraph:
    def test_build_graph_returns_compiled_graph(self):
        from orchestrator.graph import build_graph
        graph = build_graph()
        assert graph is not None

    def test_module_level_loan_graph_exists(self):
        from orchestrator.graph import loan_graph
        assert loan_graph is not None


class TestGraphNodeFunctions:
    async def test_run_applicant_profile_returns_profile_analysis(
        self, sample_application, sample_profile
    ):
        from orchestrator.graph import run_applicant_profile

        mock_agent = AsyncMock()
        mock_agent.analyze.return_value = sample_profile

        with patch("agents.applicant_profile_agent.ApplicantProfileAgent", return_value=mock_agent):
            result = await run_applicant_profile(_make_state(application=sample_application))

        assert result == {"profile_analysis": sample_profile}

    async def test_run_applicant_profile_calls_analyze_with_application(
        self, sample_application, sample_profile
    ):
        from orchestrator.graph import run_applicant_profile

        mock_agent = AsyncMock()
        mock_agent.analyze.return_value = sample_profile

        with patch("agents.applicant_profile_agent.ApplicantProfileAgent", return_value=mock_agent):
            await run_applicant_profile(_make_state(application=sample_application))

        mock_agent.analyze.assert_called_once_with(sample_application)

    async def test_run_financial_risk_returns_risk_analysis(
        self, sample_application, sample_risk
    ):
        from orchestrator.graph import run_financial_risk

        mock_agent = AsyncMock()
        mock_agent.analyze.return_value = sample_risk

        with patch("agents.financial_risk_agent.FinancialRiskAgent", return_value=mock_agent):
            result = await run_financial_risk(_make_state(application=sample_application))

        assert result == {"risk_analysis": sample_risk}

    async def test_run_loan_decision_returns_loan_decision(
        self, sample_application, sample_profile, sample_risk, sample_decision
    ):
        from orchestrator.graph import run_loan_decision

        mock_agent = AsyncMock()
        mock_agent.decide.return_value = sample_decision

        state = _make_state(
            application=sample_application,
            profile_analysis=sample_profile,
            risk_analysis=sample_risk,
        )
        with patch("agents.loan_decision_agent.LoanDecisionAgent", return_value=mock_agent):
            result = await run_loan_decision(state)

        assert result == {"loan_decision": sample_decision}

    async def test_run_loan_decision_passes_all_three_args(
        self, sample_application, sample_profile, sample_risk, sample_decision
    ):
        from orchestrator.graph import run_loan_decision

        mock_agent = AsyncMock()
        mock_agent.decide.return_value = sample_decision

        state = _make_state(
            application=sample_application,
            profile_analysis=sample_profile,
            risk_analysis=sample_risk,
        )
        with patch("agents.loan_decision_agent.LoanDecisionAgent", return_value=mock_agent):
            await run_loan_decision(state)

        mock_agent.decide.assert_called_once_with(sample_application, sample_profile, sample_risk)

    async def test_run_compliance_returns_compliance_result(
        self, sample_application, sample_decision, sample_compliance
    ):
        from orchestrator.graph import run_compliance

        mock_agent = AsyncMock()
        mock_agent.process.return_value = sample_compliance

        state = _make_state(application=sample_application, loan_decision=sample_decision)
        with patch("agents.compliance_agent.ComplianceAgent", return_value=mock_agent):
            result = await run_compliance(state)

        assert result == {"compliance_result": sample_compliance}

    async def test_run_compliance_passes_application_and_decision(
        self, sample_application, sample_decision, sample_compliance
    ):
        from orchestrator.graph import run_compliance

        mock_agent = AsyncMock()
        mock_agent.process.return_value = sample_compliance

        state = _make_state(application=sample_application, loan_decision=sample_decision)
        with patch("agents.compliance_agent.ComplianceAgent", return_value=mock_agent):
            await run_compliance(state)

        mock_agent.process.assert_called_once_with(sample_application, sample_decision)


class TestEvaluateLoan:
    def test_evaluate_loan_returns_final_state(self, sample_application, sample_decision, sample_compliance):
        from orchestrator.graph import evaluate_loan

        expected = _make_state(
            application=sample_application,
            loan_decision=sample_decision,
            compliance_result=sample_compliance,
        )

        with patch("orchestrator.graph.loan_graph") as mock_graph:
            mock_graph.ainvoke = AsyncMock(return_value=expected)
            result = evaluate_loan(sample_application)

        assert result["loan_decision"]["classification"] == "Approve"
        assert result["compliance_result"]["case_id"] == "LOAN-ABCD1234"

    def test_evaluate_loan_passes_correct_initial_state(self, sample_application):
        from orchestrator.graph import evaluate_loan

        captured = {}

        async def capture(state):
            captured["initial_state"] = state
            return state

        with patch("orchestrator.graph.loan_graph") as mock_graph:
            mock_graph.ainvoke = capture
            evaluate_loan(sample_application)

        init = captured["initial_state"]
        assert init["application"] == sample_application
        assert init["profile_analysis"] is None
        assert init["risk_analysis"] is None
        assert init["loan_decision"] is None
        assert init["compliance_result"] is None
        assert init["error"] is None

    def test_evaluate_loan_propagates_exception(self, sample_application):
        from orchestrator.graph import evaluate_loan

        with patch("orchestrator.graph.loan_graph") as mock_graph:
            mock_graph.ainvoke = AsyncMock(side_effect=ValueError("Unexpected failure"))
            with pytest.raises(ValueError, match="Unexpected failure"):
                evaluate_loan(sample_application)
