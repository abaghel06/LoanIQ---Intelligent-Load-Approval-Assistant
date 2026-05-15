"""Streamlit chatbot UI for the Intelligent Loan Approval System."""
import streamlit as st
import requests
from datetime import datetime, timezone

API_URL = "http://localhost:8000/api/loan/evaluate"

st.set_page_config(
    page_title="Intelligent Loan Approval System",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Intelligent Loan Approval System")
st.caption("Powered by Multi-Agent AI · LangGraph · Claude Sonnet 4.6")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("Loan Application")

    with st.form("loan_form"):
        applicant_id = st.text_input("Applicant ID", value="APP-001", placeholder="APP-001")
        age = st.number_input("Age", min_value=18, max_value=80, value=35)
        income = st.number_input("Annual Income (₹)", min_value=1000.0, value=750000.0, step=10000.0)
        employment_type = st.selectbox(
            "Employment Type",
            options=["Salaried", "Self-Employed", "Contract", "Unemployed"],
        )
        credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=720)
        loan_amount = st.number_input("Loan Amount (₹)", min_value=1000.0, value=1500000.0, step=10000.0)
        tenure_months = st.number_input("Loan Tenure (months)", min_value=6, max_value=360, value=60)
        existing_liabilities = st.number_input(
            "Existing Annual Liabilities (₹)", min_value=0.0, value=100000.0, step=5000.0
        )
        location = st.text_input("Location", value="Mumbai")

        submitted = st.form_submit_button("🔍 Evaluate Loan Application", use_container_width=True)

with right_col:
    st.subheader("Decision Result")

    if submitted:
        payload = {
            "applicant_id": applicant_id,
            "age": int(age),
            "income": float(income),
            "employment_type": employment_type,
            "credit_score": int(credit_score),
            "loan_amount": float(loan_amount),
            "tenure_months": int(tenure_months),
            "existing_liabilities": float(existing_liabilities),
            "location": location,
            "application_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with st.spinner("Evaluating application through AI agent pipeline..."):
            try:
                resp = requests.post(API_URL, json=payload, timeout=300)
                resp.raise_for_status()
                result = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
                st.stop()
            except requests.exceptions.Timeout:
                st.error("Request timed out. The agent pipeline is taking longer than expected.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"API error: {e.response.text}")
                st.stop()

        classification = result.get("classification", "Manual Review")
        risk_score = float(result.get("risk_score", 50))
        confidence = result.get("confidence_level", "Low")
        explanation = result.get("explanation", "")
        key_factors = result.get("key_factors", [])
        case_id = result.get("case_id", "N/A")
        timestamp = result.get("timestamp", "")
        summary = result.get("summary", "")

        if classification == "Approve":
            st.success(f"## ✅ APPROVED")
            badge_color = "green"
        elif classification == "Reject":
            st.error(f"## ❌ REJECTED")
            badge_color = "red"
        else:
            st.warning(f"## ⚠️ MANUAL REVIEW REQUIRED")
            badge_color = "orange"

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", f"{risk_score:.1f} / 100")
        col2.metric("Confidence", confidence)
        col3.metric("Case ID", case_id)

        st.markdown("---")
        st.markdown("**Decision Explanation**")
        st.info(explanation)

        if key_factors:
            st.markdown("**Key Decision Factors**")
            for factor in key_factors:
                st.markdown(f"- {factor}")

        st.markdown("---")
        st.markdown("**Compliance Summary**")
        st.caption(summary)
        if timestamp:
            st.caption(f"Processed at: {timestamp}")

    else:
        st.info("Fill in the application form on the left and click **Evaluate Loan Application** to see the AI-powered decision.")
        st.markdown("""
**How it works:**
1. Your application is sent to the FastAPI microservice
2. The LangGraph orchestrator invokes 4 specialized AI agents
3. Each agent uses its MCP server tools to analyze specific aspects
4. The final decision is synthesized and logged for compliance

**Agent Pipeline:**
- 🔎 **Applicant Profile Agent** — Income stability, employment risk, credit history
- 📊 **Financial Risk Agent** — DTI ratio, credit risk, loan amount risk, anomalies
- ⚖️ **Loan Decision Agent** — Classification, risk score, explanation
- 📋 **Compliance Agent** — Case logging, notification
""")
