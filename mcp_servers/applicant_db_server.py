"""ApplicantDB MCP Server — tools for applicant profile analysis."""
import json
from fastmcp import FastMCP

mcp = FastMCP("ApplicantDB")


@mcp.tool()
def get_income_stability_score(income: float, employment_type: str) -> float:
    """Calculate income stability score (0-100) based on income level and employment type."""
    base_scores = {
        "Salaried": 80,
        "Self-Employed": 60,
        "Contract": 50,
        "Unemployed": 10,
    }
    base = base_scores.get(employment_type, 40)

    if income >= 100000:
        income_bonus = 20
    elif income >= 60000:
        income_bonus = 10
    elif income >= 30000:
        income_bonus = 0
    elif income >= 15000:
        income_bonus = -10
    else:
        income_bonus = -20

    return float(min(100, max(0, base + income_bonus)))


@mcp.tool()
def get_employment_risk(employment_type: str) -> str:
    """Assess employment risk level based on employment type."""
    risk_map = {
        "Salaried": "Low",
        "Self-Employed": "Medium",
        "Contract": "Medium",
        "Unemployed": "High",
    }
    return risk_map.get(employment_type, "Medium")


@mcp.tool()
def get_credit_history_summary(credit_score: int) -> str:
    """Return a credit history summary dict (as JSON string) for a given credit score."""
    if credit_score >= 800:
        grade, description = "A+", "Exceptional credit history with consistent on-time payments."
    elif credit_score >= 740:
        grade, description = "A", "Very good credit with minor blemishes."
    elif credit_score >= 670:
        grade, description = "B", "Good credit, acceptable risk profile."
    elif credit_score >= 580:
        grade, description = "C", "Fair credit with some late payments or high utilization."
    elif credit_score >= 500:
        grade, description = "D", "Poor credit with significant derogatory marks."
    else:
        grade, description = "F", "Very poor credit or insufficient credit history."

    return json.dumps({"grade": grade, "description": description, "credit_score": credit_score})


@mcp.tool()
def check_application_completeness(applicant_data_json: str) -> str:
    """Check if all required application fields are present and valid. Returns JSON."""
    required_fields = [
        "applicant_id", "age", "income", "employment_type",
        "credit_score", "loan_amount", "tenure_months",
        "existing_liabilities", "location", "application_timestamp",
    ]
    try:
        data = json.loads(applicant_data_json)
    except json.JSONDecodeError:
        return json.dumps({"complete": False, "missing_fields": ["invalid JSON input"]})

    missing = [f for f in required_fields if f not in data or data[f] is None]
    invalid = []

    if "age" in data and data["age"] is not None:
        if not (18 <= int(data["age"]) <= 80):
            invalid.append("age must be between 18 and 80")
    if "credit_score" in data and data["credit_score"] is not None:
        if not (300 <= int(data["credit_score"]) <= 850):
            invalid.append("credit_score must be between 300 and 850")
    if "income" in data and data["income"] is not None:
        if float(data["income"]) < 0:
            invalid.append("income cannot be negative")
    if "loan_amount" in data and data["loan_amount"] is not None:
        if float(data["loan_amount"]) <= 0:
            invalid.append("loan_amount must be positive")

    return json.dumps({
        "complete": len(missing) == 0 and len(invalid) == 0,
        "missing_fields": missing,
        "invalid_fields": invalid,
    })


if __name__ == "__main__":
    mcp.run()
