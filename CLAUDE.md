# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agentic AI Intelligent Loan Approval System** — a multi-agent microservices application that evaluates loan applications and classifies them as **Approve**, **Reject**, or **Manual Review**. The project is built from the specification in `case-study.txt`.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (Python) |
| Microservice | FastAPI |
| Orchestration | LangGraph + LangChain |
| MCP Framework | FastMCP |
| Agent SDK | Anthropic Agent SDK |
| LLM | Claude Sonnet 4.6 (`claude-sonnet-4-6`) |

## Architecture

The system has five layers that communicate in sequence:

```
Streamlit UI → FastAPI microservice → LangGraph orchestrator → Agents (via MCP) → LLM synthesis → back to UI
```

### Agent Layer (4 agents, each with its own MCP server)

| Agent | MCP Server | Key Outputs |
|---|---|---|
| Applicant Profile Agent | `ApplicantDB` | Income stability score, employment risk, credit history summary, completeness flags |
| Financial Risk Analysis Agent | `RiskRulesDB` | Debt-to-income ratio, credit score risk level, loan amount risk, anomaly detection |
| Loan Decision Agent | `DecisionSynthesis` | Classification (Approve/Reject/Review), risk score, confidence level, key factors, explanation |
| Compliance & Action Orchestrator Agent | `NotificationSystem` | Action taken, notification sent, case ID, timestamp, summary |

### Input Schema (Loan Application)

Fields: Applicant ID, Age, Income, Employment Type, Credit Score, Loan Amount, Tenure, Existing Liabilities, Location, Application Timestamp.

## Common Commands

These commands assume a typical Python project layout. Adjust paths as the project structure is established.

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit UI
streamlit run ui/app.py

# Run FastAPI microservice
uvicorn api.main:app --reload --port 8000

# Run MCP servers (each in its own process)
python mcp_servers/applicant_db_server.py
python mcp_servers/risk_rules_server.py
python mcp_servers/decision_synthesis_server.py
python mcp_servers/notification_server.py

# Run tests
pytest

# Run a single test file
pytest tests/test_agents.py -v
```

## Implementation Notes

- Each MCP server is independent — implement them as FastMCP servers with tools that agents call.
- LangGraph manages the state graph; each node corresponds to one agent call.
- The LangGraph state object should carry the full application data plus accumulated agent outputs through the pipeline.
- Agents are implemented using the Anthropic Agent SDK with tool use; MCP servers expose the tools.
- All LLM calls use `claude-sonnet-4-6`. Include prompt caching where context is reused across agents.
- The Loan Decision Agent synthesizes outputs from the first two agents — its prompt should receive structured summaries from both upstream agents.
