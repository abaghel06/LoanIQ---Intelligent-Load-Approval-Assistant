"""RiskRulesDB MCP Server — tools for financial risk analysis."""
import json
from fastmcp import FastMCP

mcp = FastMCP("RiskRulesDB")


@mcp.tool()
def calculate_dti_ratio(income: float, loan_amount: float, existing_liabilities: float, tenure_months: int) -> float:
    """Calculate Debt-to-Income ratio as (monthly_loan_payment + existing_liabilities) / monthly_income."""
    if income <= 0:
        return 999.0
    monthly_income = income / 12
    monthly_loan_payment = loan_amount / max(tenure_months, 1)
    total_monthly_debt = monthly_loan_payment + (existing_liabilities / 12)
    return round(total_monthly_debt / monthly_income, 4)


@mcp.tool()
def assess_credit_score_risk(credit_score: int) -> str:
    """Assess risk level based on credit score."""
    if credit_score >= 740:
        return "Low"
    elif credit_score >= 670:
        return "Medium"
    elif credit_score >= 580:
        return "High"
    else:
        return "Very High"


@mcp.tool()
def assess_loan_amount_risk(loan_amount: float, income: float) -> str:
    """Assess risk based on loan-to-annual-income ratio."""
    if income <= 0:
        return "Very High"
    ratio = loan_amount / income
    if ratio <= 2:
        return "Low"
    elif ratio <= 4:
        return "Medium"
    elif ratio <= 6:
        return "High"
    else:
        return "Very High"


@mcp.tool()
def detect_anomalies(applicant_data_json: str) -> str:
    """Detect anomalies or red flags in the loan application. Returns JSON list of anomaly strings."""
    try:
        data = json.loads(applicant_data_json)
    except json.JSONDecodeError:
        return json.dumps(["invalid JSON input"])

    anomalies = []

    age = int(data.get("age", 30))
    income = float(data.get("income", 0))
    credit_score = int(data.get("credit_score", 600))
    loan_amount = float(data.get("loan_amount", 0))
    existing_liabilities = float(data.get("existing_liabilities", 0))
    employment_type = data.get("employment_type", "")
    tenure_months = int(data.get("tenure_months", 12))

    if age < 21 and loan_amount > 50000:
        anomalies.append("Very young applicant requesting a large loan amount.")
    if age > 65 and tenure_months > 120:
        anomalies.append("Applicant age + loan tenure extends beyond typical retirement horizon.")
    if employment_type == "Unemployed" and loan_amount > 10000:
        anomalies.append("Unemployed applicant requesting significant loan amount.")
    if credit_score < 500 and loan_amount > 50000:
        anomalies.append("Very poor credit score for the requested loan amount.")
    if income > 0 and existing_liabilities > income * 0.8:
        anomalies.append("Existing liabilities exceed 80% of annual income.")
    if income == 0 and employment_type != "Unemployed":
        anomalies.append("Zero income reported despite non-unemployed employment status.")

    return json.dumps(anomalies)


if __name__ == "__main__":
    mcp.run()
