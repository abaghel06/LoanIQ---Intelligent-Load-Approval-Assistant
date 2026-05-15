"""DecisionSynthesis MCP Server — tools for synthesizing a loan decision."""
import json
from fastmcp import FastMCP

mcp = FastMCP("DecisionSynthesis")


@mcp.tool()
def calculate_risk_score(profile_analysis_json: str, risk_analysis_json: str) -> float:
    """
    Calculate an overall risk score (0-100, higher = riskier) by combining
    profile and risk analysis outputs.
    """
    try:
        profile = json.loads(profile_analysis_json)
        risk = json.loads(risk_analysis_json)
    except json.JSONDecodeError:
        return 75.0

    score = 50.0

    income_stability = float(profile.get("income_stability_score", 50))
    score -= (income_stability - 50) * 0.3

    emp_risk = profile.get("employment_risk", "Medium")
    emp_adjustments = {"Low": -10, "Medium": 0, "High": 15}
    score += emp_adjustments.get(emp_risk, 0)

    dti = float(risk.get("dti_ratio", 0.4))
    if dti < 0.3:
        score -= 10
    elif dti < 0.43:
        score += 0
    elif dti < 0.5:
        score += 10
    else:
        score += 20

    credit_risk = risk.get("credit_score_risk", "Medium")
    credit_adjustments = {"Low": -15, "Medium": 0, "High": 15, "Very High": 25}
    score += credit_adjustments.get(credit_risk, 0)

    loan_risk = risk.get("loan_amount_risk", "Medium")
    loan_adjustments = {"Low": -5, "Medium": 5, "High": 15, "Very High": 25}
    score += loan_adjustments.get(loan_risk, 5)

    anomalies = risk.get("anomalies", [])
    score += len(anomalies) * 8

    completeness = profile.get("completeness_flags", {})
    if not completeness.get("complete", True):
        score += 10

    return round(min(100.0, max(0.0, score)), 2)


@mcp.tool()
def determine_classification(risk_score: float, has_anomalies: bool, completeness_ok: bool) -> str:
    """
    Determine loan classification: Approve, Reject, or Manual Review.
    """
    if not completeness_ok:
        return "Manual Review"
    if risk_score < 35:
        return "Approve"
    elif risk_score < 65:
        if has_anomalies:
            return "Manual Review"
        return "Manual Review" if risk_score > 50 else "Approve"
    else:
        return "Reject"


@mcp.tool()
def get_confidence_level(risk_score: float) -> str:
    """Return confidence level of the decision based on how decisive the risk score is."""
    if risk_score < 25 or risk_score > 80:
        return "High"
    elif risk_score < 40 or risk_score > 65:
        return "Medium"
    else:
        return "Low"


if __name__ == "__main__":
    mcp.run()
