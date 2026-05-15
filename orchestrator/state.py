"""LangGraph state definition for the loan approval pipeline."""
from typing import Optional
from typing_extensions import TypedDict


class LoanApplicationState(TypedDict):
    application: dict
    profile_analysis: Optional[dict]
    risk_analysis: Optional[dict]
    loan_decision: Optional[dict]
    compliance_result: Optional[dict]
    error: Optional[str]
