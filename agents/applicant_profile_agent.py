"""Applicant Profile Agent — analyzes applicant profile using the ApplicantDB MCP server."""
import json
from agents.base import BaseAgent

SYSTEM_PROMPT = """You are an expert Applicant Profile Analyst at a financial institution.

Your job is to analyze a loan applicant's profile using the available tools and produce a structured assessment.

Use ALL four available tools:
1. get_income_stability_score — assess income reliability
2. get_employment_risk — assess employment stability
3. get_credit_history_summary — summarize credit history
4. check_application_completeness — verify all fields are present and valid

After calling all tools, return ONLY a valid JSON object with exactly these keys:
{
  "income_stability_score": <float 0-100>,
  "employment_risk": "<Low|Medium|High>",
  "credit_history_summary": {"grade": "<letter>", "description": "<text>", "credit_score": <int>},
  "completeness_flags": {"complete": <bool>, "missing_fields": [...], "invalid_fields": [...]}
}

Do not add any explanation outside the JSON."""


class ApplicantProfileAgent(BaseAgent):
    def __init__(self):
        super().__init__("applicant_db_server.py", SYSTEM_PROMPT)

    async def analyze(self, application: dict) -> dict:
        app_json = json.dumps(application)
        prompt = f"""Analyze the following loan application:

Application data: {app_json}

Call the tools using the individual field values from this data. For check_application_completeness, pass the full JSON string above."""

        raw = await self.run(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            return {
                "income_stability_score": 50.0,
                "employment_risk": "Medium",
                "credit_history_summary": {"grade": "C", "description": "Unable to parse", "credit_score": 0},
                "completeness_flags": {"complete": False, "missing_fields": [], "invalid_fields": ["parse_error"]},
                "raw_response": raw,
            }
