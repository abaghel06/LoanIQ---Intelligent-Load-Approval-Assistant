"""Compliance & Action Orchestrator Agent — handles logging, notification, and case management."""
import json
from agents.base import BaseAgent

SYSTEM_PROMPT = """You are a Compliance Officer responsible for processing loan decisions.

Your role is to:
1. Generate a unique case ID for the decision
2. Log the decision to the compliance records
3. Prepare the applicant notification

Use ALL three available tools in sequence:
1. generate_case_id — create a unique case identifier
2. log_decision_to_file — persist the decision to the compliance log
3. format_notification_summary — prepare the applicant notification message

After calling all tools, return ONLY a valid JSON object:
{
  "action_taken": "Decision logged and notification prepared",
  "notification_sent": true,
  "case_id": "<the generated case ID>",
  "timestamp": "<ISO 8601 timestamp>",
  "summary": "<the notification message from format_notification_summary>"
}

Do not add any explanation outside the JSON."""


class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__("notification_server.py", SYSTEM_PROMPT)

    async def process(self, application: dict, loan_decision: dict) -> dict:
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        applicant_id = application.get("applicant_id", "UNKNOWN")
        classification = loan_decision.get("classification", "Manual Review")
        decision_json = json.dumps(loan_decision)

        prompt = f"""Process the compliance actions for this loan decision.

Applicant ID: {applicant_id}
Timestamp: {timestamp}
Decision: {classification}
Full Decision JSON: {decision_json}

Step 1: Call generate_case_id with applicant_id="{applicant_id}" and timestamp="{timestamp}"
Step 2: Call log_decision_to_file with the case_id from step 1, applicant_id="{applicant_id}", and decision_json={decision_json!r}
Step 3: Call format_notification_summary with decision="{classification}", applicant_id="{applicant_id}", and the case_id from step 1

Return the final JSON with timestamp="{timestamp}"."""

        raw = await self.run(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            return {
                "action_taken": "Compliance processing failed",
                "notification_sent": False,
                "case_id": f"LOAN-ERROR",
                "timestamp": timestamp,
                "summary": "Compliance processing encountered an error.",
                "raw_response": raw,
            }
