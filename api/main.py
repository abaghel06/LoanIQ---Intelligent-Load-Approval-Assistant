"""FastAPI microservice — receives loan applications and returns decisions."""
import sys
import os
import logging
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Loan Approval API", version="1.0.0")


class LoanApplication(BaseModel):
    applicant_id: str = Field(..., example="APP-001")
    age: int = Field(..., ge=18, le=80, example=35)
    income: float = Field(..., gt=0, example=75000.0)
    employment_type: str = Field(..., example="Salaried")
    credit_score: int = Field(..., ge=300, le=850, example=720)
    loan_amount: float = Field(..., gt=0, example=150000.0)
    tenure_months: int = Field(..., gt=0, example=60)
    existing_liabilities: float = Field(..., ge=0, example=10000.0)
    location: str = Field(..., example="New York")
    application_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class LoanDecisionResponse(BaseModel):
    application_id: str
    classification: str
    risk_score: float
    confidence_level: str
    key_factors: List[str]
    explanation: str
    case_id: str
    timestamp: str
    summary: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/loan/evaluate", response_model=LoanDecisionResponse)
def evaluate_loan(application: LoanApplication):
    from orchestrator.graph import evaluate_loan as run_pipeline

    app_dict = application.model_dump()

    try:
        final_state = run_pipeline(app_dict)
    except Exception as exc:
        # Unwrap Python 3.11+ ExceptionGroup to surface the real sub-exception
        real_exc = exc
        if isinstance(exc, ExceptionGroup):
            real_exc = exc.exceptions[0]
        logger.error("Pipeline error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Pipeline error: {real_exc!r}")

    decision = final_state.get("loan_decision") or {}
    compliance = final_state.get("compliance_result") or {}

    return LoanDecisionResponse(
        application_id=application.applicant_id,
        classification=decision.get("classification", "Manual Review"),
        risk_score=float(decision.get("risk_score", 50.0)),
        confidence_level=decision.get("confidence_level", "Low"),
        key_factors=decision.get("key_factors", []),
        explanation=decision.get("explanation", "No explanation available."),
        case_id=compliance.get("case_id", "N/A"),
        timestamp=compliance.get("timestamp", datetime.now(timezone.utc).isoformat()),
        summary=compliance.get("summary", ""),
    )
