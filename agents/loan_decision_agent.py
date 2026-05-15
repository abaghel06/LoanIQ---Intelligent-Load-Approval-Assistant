"""Loan Decision Agent — synthesizes a final loan decision using the DecisionSynthesis MCP server."""
import json
from agents.base import BaseAgent

SYSTEM_PROMPT = """You are a Senior Loan Officer responsible for making the final loan approval decision.

You receive a loan application along with analysis from two upstream specialists:
- Applicant Profile Analysis (income stability, employment risk, credit history)
- Financial Risk Analysis (DTI ratio, credit risk, loan risk, anomalies)

Use ALL three available tools in sequence:
1. calculate_risk_score — compute an overall risk score from the two analyses
2. determine_classification — get the Approve/Reject/Manual Review classification
3. get_confidence_level — assess how confident the decision is

After calling all tools, synthesize a final decision and return ONLY a valid JSON object:
{
  "classification": "<Approve|Reject|Manual Review>",
  "risk_score": <float 0-100>,
  "confidence_level": "<High|Medium|Low>",
  "key_factors": [<list of 3-5 key decision factors as strings>],
  "explanation": "<clear 2-3 sentence explanation of the decision reasoning>"
}

Do not add any explanation outside the JSON."""


class LoanDecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("decision_synthesis_server.py", SYSTEM_PROMPT)

    async def decide(self, application: dict, profile_analysis: dict, risk_analysis: dict) -> dict:
        profile_json = json.dumps(profile_analysis)
        risk_json = json.dumps(risk_analysis)
        has_anomalies = len(risk_analysis.get("anomalies", [])) > 0
        completeness_ok = profile_analysis.get("completeness_flags", {}).get("complete", True)

        prompt = f"""Make a loan decision for this application.

Original Application:
{json.dumps(application, indent=2)}

Profile Analysis:
{profile_json}

Financial Risk Analysis:
{risk_json}

For calculate_risk_score, pass:
- profile_analysis_json: {profile_json}
- risk_analysis_json: {risk_json}

For determine_classification, pass:
- risk_score: (the value returned by calculate_risk_score)
- has_anomalies: {str(has_anomalies).lower()}
- completeness_ok: {str(completeness_ok).lower()}

For get_confidence_level, pass the same risk_score."""

        raw = await self.run(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            return {
                "classification": "Manual Review",
                "risk_score": 50.0,
                "confidence_level": "Low",
                "key_factors": ["Unable to parse decision"],
                "explanation": "Decision synthesis failed. Manual review required.",
                "raw_response": raw,
            }
