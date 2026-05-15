"""LangGraph orchestration engine — sequential 4-agent pipeline."""
import asyncio
from langgraph.graph import StateGraph, START, END
from orchestrator.state import LoanApplicationState


async def run_applicant_profile(state: LoanApplicationState) -> dict:
    from agents.applicant_profile_agent import ApplicantProfileAgent
    agent = ApplicantProfileAgent()
    result = await agent.analyze(state["application"])
    return {"profile_analysis": result}


async def run_financial_risk(state: LoanApplicationState) -> dict:
    from agents.financial_risk_agent import FinancialRiskAgent
    agent = FinancialRiskAgent()
    result = await agent.analyze(state["application"])
    return {"risk_analysis": result}


async def run_loan_decision(state: LoanApplicationState) -> dict:
    from agents.loan_decision_agent import LoanDecisionAgent
    agent = LoanDecisionAgent()
    result = await agent.decide(
        state["application"],
        state["profile_analysis"],
        state["risk_analysis"],
    )
    return {"loan_decision": result}


async def run_compliance(state: LoanApplicationState) -> dict:
    from agents.compliance_agent import ComplianceAgent
    agent = ComplianceAgent()
    result = await agent.process(state["application"], state["loan_decision"])
    return {"compliance_result": result}


def build_graph():
    graph = StateGraph(LoanApplicationState)
    graph.add_node("profile", run_applicant_profile)
    graph.add_node("risk", run_financial_risk)
    graph.add_node("decision", run_loan_decision)
    graph.add_node("compliance", run_compliance)

    graph.add_edge(START, "profile")
    graph.add_edge("profile", "risk")
    graph.add_edge("risk", "decision")
    graph.add_edge("decision", "compliance")
    graph.add_edge("compliance", END)

    return graph.compile()


loan_graph = build_graph()


def evaluate_loan(application: dict) -> LoanApplicationState:
    """Synchronous wrapper — runs the async LangGraph pipeline and returns final state."""
    initial_state: LoanApplicationState = {
        "application": application,
        "profile_analysis": None,
        "risk_analysis": None,
        "loan_decision": None,
        "compliance_result": None,
        "error": None,
    }
    return asyncio.run(loan_graph.ainvoke(initial_state))
