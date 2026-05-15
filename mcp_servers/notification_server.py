"""NotificationSystem MCP Server — tools for compliance logging and notifications."""
import json
import os
import hashlib
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("NotificationSystem")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG_FILE = os.path.join(DATA_DIR, "decisions_log.json")


@mcp.tool()
def generate_case_id(applicant_id: str, timestamp: str) -> str:
    """Generate a unique case ID for a loan decision."""
    raw = f"{applicant_id}-{timestamp}"
    short_hash = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    return f"LOAN-{short_hash}"


@mcp.tool()
def log_decision_to_file(case_id: str, applicant_id: str, decision_json: str) -> str:
    """
    Persist the loan decision to the decisions log JSON file.
    Returns a JSON dict with status and file path.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    record = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "logged_at": datetime.utcnow().isoformat() + "Z",
        "decision": json.loads(decision_json) if isinstance(decision_json, str) else decision_json,
    }

    existing = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing.append(record)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    return json.dumps({"status": "logged", "case_id": case_id, "log_file": LOG_FILE})


@mcp.tool()
def format_notification_summary(decision: str, applicant_id: str, case_id: str) -> str:
    """Format a human-readable notification summary string for the applicant."""
    templates = {
        "Approve": (
            f"Congratulations! Loan application {case_id} for applicant {applicant_id} "
            f"has been APPROVED. Please proceed to the next steps for disbursement."
        ),
        "Reject": (
            f"We regret to inform you that loan application {case_id} for applicant "
            f"{applicant_id} has been REJECTED based on the current evaluation criteria."
        ),
        "Manual Review": (
            f"Loan application {case_id} for applicant {applicant_id} requires "
            f"MANUAL REVIEW by a loan officer. You will be contacted within 2-3 business days."
        ),
    }
    return templates.get(decision, f"Application {case_id} status: {decision}.")


if __name__ == "__main__":
    mcp.run()
