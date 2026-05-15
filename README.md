# Intelligent Loan Approval System

> A multi-agent AI microservices application that evaluates loan applications and classifies them as **Approve**, **Reject**, or **Manual Review** using a pipeline of four specialised AI agents.

**Author:** Amit Baghel · **Institution:** Wipro Technologies

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Configuration](#configuration)

---

## Overview

The Intelligent Loan Approval System automates the loan evaluation process using a pipeline of four AI agents, each with its own Model Context Protocol (MCP) server. Applications submitted through a Streamlit UI are processed by a LangGraph orchestrator, passed through each agent in sequence, and returned with a structured decision including a risk score, confidence level, and compliance case ID.

**Decision outcomes:**
| Classification | Meaning |
|---|---|
| ✅ Approve | Application meets all risk thresholds |
| ❌ Reject | Application exceeds acceptable risk limits |
| ⚠️ Manual Review | Borderline case or anomaly detected — human review required |

---

## Architecture

```
┌──────────────┐     HTTP POST      ┌───────────────────┐
│  Streamlit   │ ────────────────▶  │   FastAPI          │
│  UI          │ ◀────────────────  │   Microservice     │
└──────────────┘     JSON result    └────────┬──────────┘
                                             │
                                    ┌────────▼──────────┐
                                    │  LangGraph         │
                                    │  Orchestrator      │
                                    └────────┬──────────┘
                                             │  Sequential pipeline
                        ┌────────────────────┼────────────────────┐
                        ▼                    ▼                     ▼                     ▼
               ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐
               │ Applicant      │  │ Financial Risk  │  │ Loan Decision    │  │ Compliance &       │
               │ Profile Agent  │  │ Analysis Agent  │  │ Agent            │  │ Action Agent       │
               │ [ApplicantDB]  │  │ [RiskRulesDB]   │  │ [DecisionSynth.] │  │ [NotificationSys.] │
               └────────────────┘  └─────────────────┘  └──────────────────┘  └────────────────────┘
```

<!-- 📷 DIAGRAM PLACEHOLDER: Insert architecture diagram image here -->

### Agent Pipeline

| Step | Agent | MCP Server | Key Output |
|---|---|---|---|
| 1 | Applicant Profile Agent | `ApplicantDB` | Income stability score, employment risk, credit grade, completeness flags |
| 2 | Financial Risk Analysis Agent | `RiskRulesDB` | DTI ratio, credit risk level, loan amount risk, anomaly flags |
| 3 | Loan Decision Agent | `DecisionSynthesis` | Classification, risk score (0–100), confidence level, key factors |
| 4 | Compliance & Action Agent | `NotificationSystem` | Case ID, decision log, notification summary |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| UI | Streamlit | Latest |
| API | FastAPI + Uvicorn | Latest |
| Orchestration | LangGraph + LangChain | ≥ 0.2 / ≥ 0.3 |
| MCP Framework | FastMCP | ≥ 2.0 |
| Agent SDK | Anthropic Python SDK | ≥ 0.40.0 |
| LLM | Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| Testing | pytest + pytest-asyncio | Latest |

---

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com/))
- `pip` or a virtual environment manager

---

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd capstone

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

---

## Running the Application

The `run.sh` script starts both the FastAPI microservice and the Streamlit UI in the correct order:

```bash
bash run.sh
```

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI (REST API) | http://localhost:8000 |
| API Health Check | http://localhost:8000/health |
| API Docs (Swagger) | http://localhost:8000/docs |

To start services individually:

```bash
# FastAPI microservice
uvicorn api.main:app --reload --port 8000

# Streamlit UI (in a separate terminal)
streamlit run ui/app.py

# Individual MCP servers (each in its own terminal, if needed)
python mcp_servers/applicant_db_server.py
python mcp_servers/risk_rules_server.py
python mcp_servers/decision_synthesis_server.py
python mcp_servers/notification_server.py
```

---

## Running Tests

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_api.py -v
pytest tests/test_orchestrator.py -v
pytest tests/test_agents.py -v
```

**Test coverage summary:**

| Test Module | What it covers |
|---|---|
| `test_agents.py` | All MCP tool logic, boundary values, anomaly detection, agent class JSON parsing, fallback behaviour |
| `test_api.py` | FastAPI endpoint validation, response mapping, error handling |
| `test_orchestrator.py` | LangGraph node functions, pipeline state propagation, `evaluate_loan` wrapper |

---

## Project Structure

```
capstone/
├── agents/                         # Agent class implementations
│   ├── base.py                     # BaseAgent: MCP connection + Anthropic tool-use loop
│   ├── applicant_profile_agent.py
│   ├── financial_risk_agent.py
│   ├── loan_decision_agent.py
│   └── compliance_agent.py
├── api/
│   └── main.py                     # FastAPI app — input validation + pipeline trigger
├── mcp_servers/                    # FastMCP tool servers (one per agent)
│   ├── applicant_db_server.py
│   ├── risk_rules_server.py
│   ├── decision_synthesis_server.py
│   └── notification_server.py
├── orchestrator/
│   ├── graph.py                    # LangGraph pipeline definition
│   └── state.py                    # Shared state TypedDict
├── ui/
│   └── app.py                      # Streamlit frontend
├── tests/
│   ├── conftest.py                 # Shared pytest fixtures
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_orchestrator.py
├── data/                           # Compliance decision logs (auto-created)
├── requirements.txt
├── run.sh                          # One-command startup script
└── .env                            # API key configuration (not committed)
```

---

## API Reference

### `GET /health`

Returns service status.

```json
{ "status": "ok" }
```

### `POST /api/loan/evaluate`

Evaluates a loan application through the full AI agent pipeline.

**Request body:**

```json
{
  "applicant_id": "APP-001",
  "age": 35,
  "income": 750000.0,
  "employment_type": "Salaried",
  "credit_score": 720,
  "loan_amount": 1500000.0,
  "tenure_months": 60,
  "existing_liabilities": 100000.0,
  "location": "Mumbai",
  "application_timestamp": "2026-01-01T00:00:00Z"
}
```

**Field constraints:**

| Field | Type | Constraints |
|---|---|---|
| `age` | int | 18 – 80 |
| `income` | float | > 0 |
| `credit_score` | int | 300 – 850 |
| `loan_amount` | float | > 0 |
| `existing_liabilities` | float | ≥ 0 |
| `employment_type` | string | Salaried / Self-Employed / Contract / Unemployed |

**Response:**

```json
{
  "application_id": "APP-001",
  "classification": "Approve",
  "risk_score": 28.5,
  "confidence_level": "High",
  "key_factors": ["Stable income", "Good credit score", "Low DTI ratio"],
  "explanation": "The applicant demonstrates strong financial stability...",
  "case_id": "LOAN-A1B2C3D4",
  "timestamp": "2026-01-01T10:00:00+00:00",
  "summary": "Congratulations! Loan application LOAN-A1B2C3D4 has been APPROVED..."
}
```

---

## Configuration

Environment variables (`.env` file):

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Yes | Your Anthropic API key for Claude model access |

---

*Intelligent Loan Approval System · Amit Baghel · Wipro Technologies*
