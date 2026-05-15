"""Financial Risk Analysis Agent — evaluates financial risk using the RiskRulesDB MCP server."""
import json
from agents.base import BaseAgent

SYSTEM_PROMPT = """You are a Financial Risk Analyst at a lending institution.

Your responsibility is to evaluate the financial risk of a loan application using the available tools.

Use ALL four available tools:
1. calculate_dti_ratio — compute the debt-to-income ratio
2. assess_credit_score_risk — evaluate credit score risk level
3. assess_loan_amount_risk — evaluate whether the loan amount is appropriate for the income
4. detect_anomalies — identify any red flags or unusual patterns

After calling all tools, return ONLY a valid JSON object with exactly these keys:
{
  "dti_ratio": <float>,
  "credit_score_risk": "<Low|Medium|High|Very High>",
  "loan_amount_risk": "<Low|Medium|High|Very High>",
  "anomalies": [<list of anomaly strings, empty if none>],
  "reasoning": "<brief 1-2 sentence financial risk summary>"
}

Do not add any explanation outside the JSON."""


class FinancialRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("risk_rules_server.py", SYSTEM_PROMPT)

    async def analyze(self, application: dict) -> dict:
        app_json = json.dumps(application)
        prompt = f"""Evaluate the financial risk of this loan application:

Application data: {app_json}

For calculate_dti_ratio, use: income={application.get('income')}, loan_amount={application.get('loan_amount')}, existing_liabilities={application.get('existing_liabilities')}, tenure_months={application.get('tenure_months')}.
For detect_anomalies, pass the full JSON string above."""

        raw = await self.run(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            return {
                "dti_ratio": 0.5,
                "credit_score_risk": "Medium",
                "loan_amount_risk": "Medium",
                "anomalies": [],
                "reasoning": "Unable to parse risk analysis.",
                "raw_response": raw,
            }
