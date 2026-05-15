# Intelligent Loan Approval System — User Manual

**Author:** Amit Baghel · **Institution:** Wipro Technologies  
**Version:** 1.0 · **Document Type:** User Manual

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [For End Users — Using the Web Interface](#2-for-end-users--using-the-web-interface)
   - 2.1 [Accessing the System](#21-accessing-the-system)
   - 2.2 [Application Form — Field Guide](#22-application-form--field-guide)
   - 2.3 [Submitting an Application](#23-submitting-an-application)
   - 2.4 [Understanding the Decision Result](#24-understanding-the-decision-result)
   - 2.5 [Reading the Risk & Compliance Details](#25-reading-the-risk--compliance-details)
3. [For Technical Users — Installation & Setup](#3-for-technical-users--installation--setup)
   - 3.1 [System Requirements](#31-system-requirements)
   - 3.2 [Installation Steps](#32-installation-steps)
   - 3.3 [Starting the Application](#33-starting-the-application)
   - 3.4 [Environment Configuration](#34-environment-configuration)
   - 3.5 [Running in Development Mode](#35-running-in-development-mode)
4. [Troubleshooting](#4-troubleshooting)
5. [Glossary](#5-glossary)

---

## 1. System Overview

The **Intelligent Loan Approval System** is an AI-powered platform that evaluates loan applications automatically. When a loan officer or applicant submits an application, the system passes it through a pipeline of four specialised AI agents — each analysing a different aspect of the application — before returning a decision.

**What the system does:**
- Analyses the applicant's financial profile and credit history
- Calculates the debt-to-income ratio and flags anomalies
- Produces a risk score between 0 (very low risk) and 100 (very high risk)
- Classifies the application as **Approve**, **Reject**, or **Manual Review**
- Generates a compliance case ID and logs the decision

**What the system does not do:**
- It does not access real bank databases or credit bureaus
- It does not send actual email or SMS notifications
- It does not make legally binding decisions (always subject to human review)

<!-- 📷 SCREENSHOT PLACEHOLDER: Insert screenshot of the full UI here -->

---

## 2. For End Users — Using the Web Interface

### 2.1 Accessing the System

Open your web browser and navigate to:

```
http://localhost:8501
```

You will see a two-panel interface:
- **Left panel** — the loan application form
- **Right panel** — the decision result (displayed after submission)

> If you see a blank page or connection error, the system may not be running. Contact your system administrator or refer to [Section 3.3](#33-starting-the-application).

<!-- 📷 SCREENSHOT PLACEHOLDER: Insert screenshot of the landing page -->

---

### 2.2 Application Form — Field Guide

Fill in all fields in the left panel before submitting.

| Field | What to Enter | Example |
|---|---|---|
| **Applicant ID** | A unique identifier for this application | `APP-001`, `CUST-2024-08` |
| **Age** | Applicant's age in years (18–80) | `35` |
| **Annual Income (₹)** | Total annual income before tax, in Indian Rupees | `750000` |
| **Employment Type** | Select from the dropdown | Salaried, Self-Employed, Contract, Unemployed |
| **Credit Score** | Credit score on the 300–850 scale | `720` |
| **Loan Amount (₹)** | The amount being requested, in Indian Rupees | `1500000` |
| **Loan Tenure (months)** | Repayment period in months | `60` (= 5 years) |
| **Existing Annual Liabilities (₹)** | Total annual debt obligations already held | `100000` |
| **Location** | City or region of the applicant | `Mumbai` |

**Important notes:**
- All monetary values are in **Indian Rupees (₹)**
- Age must be between **18 and 80**
- Credit score must be between **300 and 850**
- Income and Loan Amount must be greater than zero
- Existing liabilities can be zero if the applicant has no current debt

<!-- 📷 SCREENSHOT PLACEHOLDER: Insert annotated screenshot of the form with callouts -->

---

### 2.3 Submitting an Application

Once all fields are filled in, click the button:

> **🔍 Evaluate Loan Application**

The system will process the application through its AI agent pipeline. This typically takes **15–60 seconds** depending on API response times. A spinner will appear while processing is in progress.

> **Do not close the browser tab while the spinner is active.** The process cannot be resumed once interrupted.

---

### 2.4 Understanding the Decision Result

The right panel will display one of three outcomes:

---

#### ✅ APPROVED

> The application has been evaluated favourably. The risk score is below the acceptance threshold and no significant anomalies were detected.

What this means in practice: the AI agents found that the applicant has sufficient income stability, an acceptable credit history, and a manageable debt-to-income ratio relative to the loan amount requested.

---

#### ❌ REJECTED

> The application exceeds the risk threshold. Common reasons include a very high risk score, very poor credit history, or a loan amount far exceeding income.

What this means in practice: the system determined the combination of risk factors makes this application unsuitable for approval under standard criteria.

---

#### ⚠️ MANUAL REVIEW REQUIRED

> The application falls in a borderline zone or contains anomalies that require human judgement. A loan officer will need to review this case.

What this means in practice: the system is not confident enough to approve or reject automatically. This could be due to unusual circumstances (e.g., high income but very short employment history), missing data, or a risk score that sits between the approve and reject thresholds.

<!-- 📷 SCREENSHOT PLACEHOLDER: Insert screenshots of all three decision outcomes side by side -->

---

### 2.5 Reading the Risk & Compliance Details

Below the main decision banner, three metric cards are displayed:

| Metric | What it means |
|---|---|
| **Risk Score** | A number from 0 to 100. Lower is better. Below 35 = low risk; above 65 = high risk. |
| **Confidence** | How decisive the score is: **High** (score far from boundaries), **Medium**, or **Low** (score near a threshold). |
| **Case ID** | A unique reference number (e.g., `LOAN-A1B2C3D4`) for this decision, used for compliance records. |

**Decision Explanation** — a plain-English summary of why the decision was made, produced by the Loan Decision Agent.

**Key Decision Factors** — a bulleted list of the top 3–5 factors that most influenced the decision (e.g., "High debt-to-income ratio", "Stable employment history").

**Compliance Summary** — the notification message that would be sent to the applicant, along with the exact timestamp of processing.

<!-- 📷 SCREENSHOT PLACEHOLDER: Insert annotated screenshot of the results panel -->

---

## 3. For Technical Users — Installation & Setup

### 3.1 System Requirements

| Requirement | Minimum |
|---|---|
| Operating System | Linux, macOS, or Windows 10+ |
| Python | 3.10 or higher |
| RAM | 4 GB (8 GB recommended) |
| Internet | Required (API calls to Anthropic) |
| Anthropic API Key | Required |

---

### 3.2 Installation Steps

```bash
# Step 1: Clone the repository
git clone <repository-url>
cd capstone

# Step 2: Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Step 3: Install all dependencies
pip install -r requirements.txt

# Step 4: Set up the environment file
cp .env.example .env
```

Open `.env` in a text editor and set your API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

### 3.3 Starting the Application

**One-command start (recommended):**

```bash
bash run.sh
```

This starts the FastAPI server first, waits for it to become healthy, then starts the Streamlit UI.

**Manual start (two terminals):**

```bash
# Terminal 1 — FastAPI
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Streamlit
streamlit run ui/app.py
```

**Verify the system is running:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

---

### 3.4 Environment Configuration

| Variable | Description | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude model access | ✅ Yes |

The `.env` file is loaded automatically at startup via `python-dotenv`. Never commit this file to version control.

---

### 3.5 Running in Development Mode

```bash
# Run with auto-reload on code changes
uvicorn api.main:app --reload --port 8000

# Run the full test suite
pytest -v

# Run only a specific test module
pytest tests/test_api.py -v
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v
```

Decision logs are written to `data/decisions_log.json` automatically after each evaluation. This file is created on first use.

---

## 4. Troubleshooting

| Symptom | Likely Cause | Resolution |
|---|---|---|
| "Cannot connect to the API" in the UI | FastAPI server is not running | Run `bash run.sh` or start FastAPI manually |
| "Request timed out" in the UI | Anthropic API is slow or key is invalid | Check your API key in `.env`; retry after a moment |
| Spinner runs for more than 2 minutes | Network issue or API quota exceeded | Check Anthropic console for quota limits |
| `ANTHROPIC_API_KEY` not set error | `.env` file missing or empty | Copy `.env.example` to `.env` and add your key |
| `ModuleNotFoundError` on startup | Dependencies not installed | Run `pip install -r requirements.txt` |
| All applications show "Manual Review" | Likely a parsing error in agents | Check terminal logs for JSON parse warnings |
| `data/decisions_log.json` not created | No submissions have been made yet | Submit at least one application |

---

## 5. Glossary

| Term | Definition |
|---|---|
| **Agent** | An AI module that uses tools (via an MCP server) to analyse one aspect of the loan application |
| **MCP Server** | Model Context Protocol server — exposes tools that an agent can call |
| **LangGraph** | Orchestration framework that manages the sequential flow between agents |
| **DTI Ratio** | Debt-to-Income ratio — total monthly debt payments divided by monthly income |
| **Risk Score** | A composite score (0–100) calculated from profile, financial, and anomaly data |
| **Confidence Level** | How far the risk score is from a decision boundary (High / Medium / Low) |
| **Case ID** | A unique identifier generated for each decision, used for compliance logging |
| **Prompt Caching** | A technique that reuses system prompts across API calls to reduce latency and cost |
| **Claude Sonnet 4.6** | The Anthropic LLM used by all four agents for reasoning and synthesis |

---

*Intelligent Loan Approval System · User Manual v1.0 · Amit Baghel · Wipro Technologies*
