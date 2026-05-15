# Intelligent Loan Approval System — Demo & Presentation Guide

**Presenter:** Amit Baghel · **Institution:** Wipro Technologies  
**Presentation Type:** Capstone / Academic Demonstration  
**Suggested Duration:** 20–25 minutes + Q&A

---

## Presentation Overview

| Section | Topic | Time |
|---|---|---|
| 1 | Problem Statement & Motivation | 2 min |
| 2 | Solution Overview | 3 min |
| 3 | System Architecture Deep Dive | 4 min |
| 4 | Live Demo | 7 min |
| 5 | Technical Highlights | 4 min |
| 6 | Results & Evaluation | 3 min |
| 7 | Q&A | 5–10 min |

---

## Section 1 — Problem Statement & Motivation

### What to Show
- An opening slide with the problem framed as a business and technical challenge.

<!-- 📊 SLIDE PLACEHOLDER: "The Problem with Traditional Loan Approval" — show a manual process flowchart with delays highlighted -->

### Key Points
- Traditional loan approval is slow, inconsistent, and resource-intensive
- Human officers must evaluate dozens of data points per application
- Inconsistency in decisions leads to compliance risk
- There is no scalable way to process high volumes of applications with uniform criteria

### Speaker Notes
> *"Banks and financial institutions process thousands of loan applications every day. Each application requires a loan officer to manually verify income stability, calculate debt ratios, check credit history, and document the decision for compliance. This process is slow — often taking days — and introduces human inconsistency. Two officers evaluating the same application can reach different conclusions."*

> *"The question this project answers is: can we use modern agentic AI to replicate — and improve — this evaluation process? Not to replace human judgement entirely, but to automate the routine analysis and flag only the borderline cases for human review."*

---

## Section 2 — Solution Overview

### What to Show
- A high-level diagram showing: Applicant → UI → API → Agents → Decision

<!-- 📊 SLIDE PLACEHOLDER: "Our Solution — Intelligent Loan Approval System" — show the 5-layer pipeline diagram -->

### Key Points
- The system uses **four specialised AI agents**, each responsible for one dimension of the evaluation
- Agents communicate through **MCP (Model Context Protocol) servers** — a standardised tool interface for AI agents
- The pipeline is orchestrated by **LangGraph**, ensuring sequential and stateful execution
- The LLM backbone is **Claude Sonnet 4.6** — Anthropic's production-grade model with tool-use capability

### Speaker Notes
> *"Our solution is the Intelligent Loan Approval System — a multi-agent AI application built on Anthropic's Claude Sonnet 4.6. Rather than a single model trying to do everything, we decompose the problem into four distinct expert agents: one for applicant profiling, one for financial risk analysis, one for decision synthesis, and one for compliance logging."*

> *"Each agent has access to its own set of business-logic tools through MCP servers. This separation means each agent's reasoning is focused, auditable, and independently testable."*

---

## Section 3 — System Architecture Deep Dive

### What to Show
- The full architecture diagram with all five layers labelled
- A table showing each agent and its MCP tools

<!-- 📊 SLIDE PLACEHOLDER: Full architecture diagram — Streamlit → FastAPI → LangGraph → 4 Agents → MCP Servers -->
<!-- 📊 SLIDE PLACEHOLDER: Agent-tool mapping table -->

### Key Points

**Layer 1 — Streamlit UI**
- Web form for submitting loan applications
- Displays structured decision results with metrics

**Layer 2 — FastAPI Microservice**
- Validates input (age, credit score bounds, income constraints)
- Triggers the LangGraph pipeline and returns the result

**Layer 3 — LangGraph Orchestrator**
- Manages a stateful graph of four sequential nodes
- Each node calls one agent; outputs accumulate in shared state

**Layer 4 — AI Agents (×4)**

| Agent | MCP Server | Responsibility |
|---|---|---|
| Applicant Profile | ApplicantDB | Income stability score, employment risk, credit grade |
| Financial Risk | RiskRulesDB | DTI ratio, credit risk, loan amount risk, anomaly detection |
| Loan Decision | DecisionSynthesis | Risk score (0–100), classification, confidence level |
| Compliance | NotificationSystem | Case ID generation, decision logging, notification |

**Layer 5 — Anthropic Claude API**
- All agents use Claude Sonnet 4.6 with prompt caching
- Tool-use loop: agent calls tool → gets result → continues reasoning → returns JSON

### Speaker Notes
> *"Let me walk you through the architecture. At the top is a Streamlit web interface — a clean form where a loan officer enters the applicant's details. This submits to a FastAPI microservice, which validates the input and triggers the LangGraph orchestrator."*

> *"LangGraph manages the pipeline as a directed graph with four nodes. State flows from left to right: first the Applicant Profile Agent runs, then Financial Risk, then the Loan Decision Agent — which synthesises the first two outputs — and finally the Compliance Agent logs the result and prepares the notification."*

> *"Each agent connects to its own MCP server — a lightweight Python process that exposes business logic as callable tools. This is important: the tools contain deterministic rule-based logic, while the LLM handles reasoning, synthesis, and natural language explanation."*

---

## Section 4 — Live Demo

### Pre-Demo Checklist
- [ ] Application is running: `bash run.sh`
- [ ] Browser open at `http://localhost:8501`
- [ ] API health confirmed: `curl http://localhost:8000/health`
- [ ] Network connection active (API calls required)

<!-- 📷 SCREENSHOT PLACEHOLDER: Browser showing the Streamlit UI ready for input -->

### Demo Scenario 1 — Strong Applicant (Expected: Approve)

Fill in the form with these values:

| Field | Value |
|---|---|
| Applicant ID | `DEMO-APPROVE-01` |
| Age | `34` |
| Annual Income (₹) | `1200000` |
| Employment Type | `Salaried` |
| Credit Score | `780` |
| Loan Amount (₹) | `1500000` |
| Loan Tenure | `60 months` |
| Existing Liabilities (₹) | `50000` |
| Location | `Bangalore` |

**Expected Result:** ✅ Approve · Risk Score ~20–30 · Confidence: High

### Speaker Notes for Demo 1
> *"Let's start with a strong applicant. This is someone with a ₹12 lakh annual salary, a credit score of 780, and requesting a ₹15 lakh loan over 5 years. They have minimal existing liabilities. I'll click Evaluate and we'll watch the pipeline run in real time."*

> *[While processing]* *"Behind the scenes, four AI agents are running sequentially. The first agent is calling MCP tools to compute this applicant's income stability score and credit grade. That result feeds into the financial risk agent, which is calculating the debt-to-income ratio..."*

> *[After result appears]* *"Approved — with a risk score of around 25 and high confidence. You can see the key factors: stable salaried employment, excellent credit score, and a low debt-to-income ratio. The compliance agent has logged this with a unique case ID, and the notification is ready."*

---

### Demo Scenario 2 — High-Risk Applicant (Expected: Reject)

| Field | Value |
|---|---|
| Applicant ID | `DEMO-REJECT-01` |
| Age | `42` |
| Annual Income (₹) | `200000` |
| Employment Type | `Unemployed` |
| Credit Score | `420` |
| Loan Amount (₹) | `2000000` |
| Loan Tenure | `120 months` |
| Existing Liabilities (₹) | `180000` |
| Location | `Delhi` |

**Expected Result:** ❌ Reject · Risk Score ~85–95 · Confidence: High

### Speaker Notes for Demo 2
> *"Now let's look at the opposite end of the spectrum — an unemployed applicant with a very poor credit score requesting ₹20 lakh with existing liabilities already near 90% of their declared income. The anomaly detection in the financial risk agent should flag several issues here."*

> *[After result]* *"Rejected — risk score in the high 80s. The key factors tell the story clearly: unemployed status, very poor credit history, loan amount well beyond income, and the system detected an anomaly around existing liabilities exceeding 80% of annual income."*

---

### Demo Scenario 3 — Borderline Case (Expected: Manual Review)

| Field | Value |
|---|---|
| Applicant ID | `DEMO-REVIEW-01` |
| Age | `28` |
| Annual Income (₹) | `480000` |
| Employment Type | `Contract` |
| Credit Score | `620` |
| Loan Amount (₹) | `1400000` |
| Loan Tenure | `84 months` |
| Existing Liabilities (₹) | `120000` |
| Location | `Pune` |

**Expected Result:** ⚠️ Manual Review · Risk Score ~50–60 · Confidence: Low

### Speaker Notes for Demo 3
> *"The most interesting scenario is the borderline case. Contract employment, a fair credit score, and a loan amount that's about 3× the annual income. The system should be uncertain here — and that's by design. A low-confidence, mid-range risk score means the system defers to a human loan officer rather than making a potentially wrong automated decision."*

> *"This is a deliberate design choice: AI makes the easy decisions automatically and flags the hard ones for human review. That's the right division of labour."*

---

## Section 5 — Technical Highlights

### What to Show
- Code snippet: MCP tool example from `risk_rules_server.py`
- Code snippet: LangGraph pipeline from `graph.py`
- Test results output from `pytest -v`

<!-- 📊 SLIDE PLACEHOLDER: Code snippet — `calculate_dti_ratio` tool -->
<!-- 📊 SLIDE PLACEHOLDER: Code snippet — `build_graph()` LangGraph pipeline -->
<!-- 📊 SLIDE PLACEHOLDER: pytest output showing 107 tests passing -->

### Key Points

**1. Separation of concerns via MCP**
- Business rules (DTI calculation, anomaly thresholds, classification logic) live in MCP tools — deterministic, testable Python functions
- LLM reasoning lives in agents — synthesis, explanation, and tool orchestration

**2. Prompt caching for cost efficiency**
- System prompts are marked `ephemeral` in the Anthropic API call, enabling server-side prompt caching
- Reduces token cost and latency for repeated calls with the same agent configuration

**3. Structured JSON outputs with fallback**
- Each agent extracts a JSON object from the LLM response
- If parsing fails, a safe fallback value is returned — the pipeline never crashes

**4. Comprehensive test coverage**
- 107 unit tests across MCP tools, agent classes, API endpoints, and orchestrator nodes
- Agent tests use `AsyncMock` to mock `BaseAgent.run()` — no live API calls required

### Speaker Notes
> *"A few technical choices I want to highlight. First, the architecture deliberately separates deterministic business logic from AI reasoning. The MCP tools contain the actual rules — the DTI formula, the anomaly thresholds, the classification boundaries. The LLM reads the tool outputs and synthesises an explanation. This means the business rules are auditable and unit-testable without touching the AI layer."*

> *"Second, I'm using Anthropic's prompt caching feature. The system prompts for each agent are marked as ephemeral, which allows the API to cache them across calls. In a production system processing hundreds of applications, this significantly reduces both cost and latency."*

> *"Finally, the test suite. 107 tests — covering every MCP tool, every classification boundary condition, all four agent classes, the API validation layer, and the LangGraph orchestrator. All tests pass, and none of them make live API calls — the agents are tested with mocked LLM responses."*

---

## Section 6 — Results & Evaluation

### What to Show
- Summary table of decision logic
- Test results screenshot
- Architecture recap

<!-- 📊 SLIDE PLACEHOLDER: Risk score → classification threshold diagram -->
<!-- 📊 SLIDE PLACEHOLDER: pytest results screenshot — 107 passed -->

### Key Points

**Classification thresholds:**

| Risk Score Range | Outcome |
|---|---|
| < 35 | ✅ Approve |
| 35–50 (no anomalies) | ✅ Approve |
| 35–65 (with anomalies or score > 50) | ⚠️ Manual Review |
| ≥ 65 | ❌ Reject |
| Incomplete application | ⚠️ Manual Review |

**What was achieved:**
- ✅ Full 4-agent pipeline operational end-to-end
- ✅ 107 unit tests passing
- ✅ FastAPI with Pydantic validation
- ✅ Compliance logging to persistent JSON file
- ✅ Prompt caching implemented across all agents
- ✅ INR currency support in UI
- ✅ Structured fallback for all agent outputs

### Speaker Notes
> *"To summarise: the system correctly classifies applications across all three outcomes, with the risk thresholds calibrated to produce meaningful distinctions. The test suite validates the classification logic at each boundary — including the edge case at score 50, which sits exactly on the Approve/Manual Review boundary depending on anomaly flags."*

> *"From a technical delivery perspective: the full pipeline runs end-to-end, all four agents are functional, the API validates inputs correctly, and the test suite gives high confidence in the correctness of the business logic."*

---

## Section 7 — Anticipated Q&A

**Q: Why four separate agents instead of one prompt to a single LLM?**
> Each agent is focused on a single domain — applicant profiling, financial risk, decision synthesis, compliance. This means each agent's system prompt can be tightly scoped, the tools it calls are relevant to its task, and the outputs are structured and predictable. A single monolithic prompt would produce less reliable structured JSON across 10+ tool calls and be much harder to test or debug.

**Q: How does MCP improve this over direct function calls?**
> MCP provides a standardised protocol for AI agents to discover and call tools. It allows the agent to list available tools at runtime rather than having them hardcoded. This makes each agent's tool interface independently deployable and swappable — a different risk model could be plugged in by swapping the MCP server without touching the agent code.

**Q: How would this scale to production?**
> The MCP servers are stateless Python processes — they can be containerised and run behind a load balancer. The FastAPI layer can be horizontally scaled. The LangGraph pipeline is already async-ready. The main production consideration would be Anthropic API rate limits and latency, which would be addressed with request queuing and potentially asynchronous processing.

**Q: Why is the Manual Review band so wide?**
> Deliberately so. In a real lending context, the cost of a wrong rejection (lost business) and a wrong approval (default) are both significant. A conservative band around the decision boundary ensures that genuinely ambiguous cases go to a human rather than being decided by a model with low confidence. The band can be tuned by adjusting the threshold constants in `decision_synthesis_server.py`.

**Q: How are the risk score thresholds determined?**
> The current thresholds are illustrative rule-based values designed for this demonstration. In a production system, these would be calibrated against historical loan performance data using a credit risk modelling framework. The MCP architecture makes this easy to update — the thresholds live in one file and the agents automatically use the updated values.

**Q: What happens if the Anthropic API is unavailable?**
> Each agent has a fallback: if the LLM response cannot be parsed as valid JSON, a safe default value is returned (e.g., "Manual Review" with 50% risk score). The pipeline continues rather than crashing. In production, a circuit breaker pattern and retry logic would be added at the `BaseAgent.run()` level.

---

## Appendix A — Quick Reference

### Application Flow (For reference during Q&A)

```
User submits form
       ↓
FastAPI validates fields (age, credit_score, income, etc.)
       ↓
LangGraph initialises state with application data
       ↓
Node 1: ApplicantProfileAgent → income_stability_score, employment_risk, credit_grade
       ↓
Node 2: FinancialRiskAgent → dti_ratio, credit_score_risk, anomalies
       ↓
Node 3: LoanDecisionAgent → risk_score, classification, explanation
       ↓
Node 4: ComplianceAgent → case_id, log entry, notification summary
       ↓
FastAPI returns LoanDecisionResponse to Streamlit
       ↓
UI displays decision with all metadata
```

### Risk Score Calculation (Key Adjustments)

| Factor | Effect on Score |
|---|---|
| High income stability (>50) | Decreases score |
| Employment risk: Low / High | −10 / +15 |
| DTI ratio < 0.3 / > 0.5 | −10 / +20 |
| Credit risk: Low / Very High | −15 / +25 |
| Loan amount risk: Low / Very High | −5 / +25 |
| Each anomaly detected | +8 |
| Incomplete application | +10 |

---

*Intelligent Loan Approval System · Demo Guide v1.0 · Amit Baghel · Wipro Technologies*
