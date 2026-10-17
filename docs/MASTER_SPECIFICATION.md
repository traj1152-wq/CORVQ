# CORVQ — Master Project Specification
**Project:** CORVQ  
**Product Name:** Adaptive Agentic Intelligence & Governance Platform  
**Tagline:** One Intelligence Engine. Every Industry.  
**Hackathon:** Hack2Skill AI Builder Cup  
**Category:** Future of Work & Enterprise Productivity  
**Development:** VS Code + OpenAI Codex  
**Repository:** GitHub  
**Target Deployment:** Google Cloud Run + Firebase Hosting  

---

## 1. PROJECT VISION

We are building **CORVQ**, an industry-adaptive AI platform that helps organisations investigate complex problems, detect risks, analyse evidence, verify AI-generated conclusions, and make reliable, explainable decisions.

CORVQ should work across multiple industries using one reusable intelligence engine.

Instead of building separate AI applications for banking, e-commerce, healthcare, manufacturing, and other sectors, CORVQ will use a **modular industry-adapter architecture**.

Each industry provides its own data schemas, business rules, and evidence validators. The core investigation engine remains reusable.

Our hackathon MVP will demonstrate adaptability through two fully functioning industry modules:

1. **Banking:** Financial fraud and suspicious transaction investigation.
2. **E-commerce:** Suspicious orders, seller risks, and transaction-pattern investigation.

Future industries can be added through adapters without rewriting the entire platform.

Our central innovation is **ProofGuard**, an evidence-verification and counterfactual-analysis engine designed to challenge unsupported AI conclusions.

---

## 2. THE PROBLEM WE ARE SOLVING

Organisations increasingly depend on AI to analyse information and support decisions.

However, AI-generated recommendations can contain hallucinations, incorrect interpretations, unsupported conclusions, or misleading explanations.

Enterprise teams also struggle with fragmented workflows, scattered evidence, repetitive investigations, and complex governance processes.

We want to address five challenges:

1. AI conclusions are not always verifiable.
2. Organisations spend time manually reviewing evidence.
3. Different industries require different investigation rules.
4. AI systems need monitoring, security, and human oversight.
5. Building separate AI solutions for every industry is expensive and difficult to maintain.

**Our solution:** One reusable AI investigation platform that combines domain-specific analysis, agentic AI, evidence verification, counterfactual testing, and auditable human decisions.

---

## 3. CORE PRODUCT CAPABILITIES

### A. Adaptive Industry Engine

Users select an industry from the dashboard.

The system loads the corresponding data schema, investigation rules, evaluation logic, and relevant policy knowledge.

Initial adapters:

**Banking Adapter**
- Analyse banking transactions.
- Identify unusual transaction amounts and frequency.
- Detect suspicious account relationships.
- Visualise connected accounts.
- Investigate potential circular fund transfers.
- Explain findings with transaction-level evidence.

**E-commerce Adapter**
- Analyse orders and seller records.
- Identify suspicious order patterns.
- Detect abnormal purchasing or refund activity.
- Analyse seller and customer relationships.
- Investigate unusual order or payment behaviour.
- Explain findings with order-level evidence.

Both adapters must use the same shared investigation workflow.

### B. CORVQ Core Investigation Engine

The shared engine should:

1. Accept structured industry data.
2. Validate incoming records.
3. Apply the selected industry's analysis rules.
4. Produce structured risk indicators and evidence references.
5. Coordinate Gemini-powered investigation agents.
6. Verify generated factual claims.
7. Perform optional counterfactual analysis.
8. Generate an investigation report.
9. Request human review.
10. Store results and audit history.

### C. Gemini Multi-Agent AI

Use **Gemini** and **Google Agent Development Kit (ADK)**.

Build reusable agent roles:

**Investigation Agent:** Analyses available risk indicators and investigation data.

**Relationship Agent:** Explains connections among accounts, users, transactions, or orders.

**Policy Agent:** Reviews relevant supplied policies and explains applicable controls with source references.

**Report Agent:** Generates structured investigation reports and recommended next steps.

**Orchestrator:** Coordinates agent execution and collects the results.

The agents must use actual evidence returned by the backend tools.

Do not fabricate evidence, transactions, policies, or API responses.

### D. ProofGuard — Evidence Verification

This is the central differentiating feature.

When Gemini produces factual claims, ProofGuard must independently verify them against the structured evidence.

For example:

AI claim: "Account A transferred ₹50,000 to Account B."

ProofGuard must locate the corresponding transaction record and validate the sender, recipient, and amount.

Verification statuses:

- **Verified:** The claim is supported by the referenced evidence.
- **Unsupported:** The records do not support the claim.
- **Needs Review:** The claim cannot be resolved reliably from available evidence.

Use deterministic Python validation wherever possible instead of trusting another LLM to verify facts.

Each verification result must include a reference to the supporting or conflicting record.

### E. Counterfactual Investigation Engine

Allow users to change or remove selected evidence and rerun the analysis.

Example:

The banking engine identifies a circular transfer involving Accounts A, B, and C.

The user removes the transaction from C back to A.

The system must recalculate the graph and update the circular-transfer finding.

The same mechanism should work for e-commerce investigation scenarios.

Counterfactual tests must recalculate findings using modified data, not display hardcoded answers.

### F. AI Governance

Implement:

- Human review and approval.
- Evidence traceability.
- Explainable risk findings.
- Investigation history.
- Recorded decisions.
- Audit logs.
- Role-based access design.
- Clear separation of verified facts, risk indicators, and AI hypotheses.

AI must not independently execute high-impact actions such as freezing bank accounts, accusing individuals of crimes, or suspending sellers.

### G. LLMOps

Implement practical monitoring and evaluation of our AI workflows:

- Model and prompt version tracking.
- Structured output validation.
- Grounding and evidence-accuracy tests.
- Unsupported-claim detection.
- Response latency monitoring.
- API error monitoring.
- Token usage and cost tracking where available.
- Regression tests using known synthetic scenarios.

### H. DevSecOps

Use automated security practices:

- GitHub Actions CI.
- Python and frontend tests.
- Static analysis.
- Dependency scanning.
- Secret scanning.
- Container scanning where configured.
- Environment-based configuration.
- Secure credential management.
- Appropriate API authentication and access control.

---

## 4. TECHNOLOGY STACK

| Component | Technology |
|---|---|
| Coding Environment | VS Code + OpenAI Codex |
| Source Control | Git + GitHub |
| Frontend | React + Vite + Tailwind CSS |
| Visualisation | React Flow |
| Backend | Python + FastAPI |
| Data Validation | Pydantic |
| Data Processing | Pandas |
| Risk Detection | Python rules + optional Scikit-learn |
| Relationship Analysis | NetworkX |
| AI Reasoning | Gemini |
| Agent Framework | Google ADK |
| Local Database | SQLite |
| Cloud Database | Google Cloud Firestore |
| Frontend Deployment | Firebase Hosting |
| Backend Deployment | Google Cloud Run |
| DevSecOps | GitHub Actions + Semgrep + pip-audit + Trivy |
| LLMOps | Pytest + AI evaluation tests + Cloud Logging |

Keep the architecture modular.

Do not introduce unnecessary services, frameworks, or infrastructure.

---

## 5. SYSTEM ARCHITECTURE

**Frontend**

React application containing:
- Overview dashboard
- Industry selection
- Dataset upload / sample selection
- Investigation workspace
- Findings and risk explanations
- Relationship graph
- ProofGuard evidence verification
- Counterfactual analysis
- Human review
- Audit history

**Backend**

Python FastAPI application providing:
- REST APIs
- Input validation
- Industry-adapter management
- Investigation orchestration
- Rule-based detection
- Relationship analysis
- Gemini agent integration
- ProofGuard verification
- Counterfactual recalculation
- Report generation
- Audit and approval operations

**Data Layer**

Use SQLite for local development.

Provide a repository abstraction so Firestore can be integrated for cloud deployment.

**AI Layer**

Use Gemini through an authorized API connection.

Google ADK should orchestrate agents through backend-only tools and services.

No API keys should be embedded in frontend code.

---

## 6. EXPECTED USER WORKFLOW

**Step 1:** User opens the CORVQ dashboard.

**Step 2:** User selects Banking or E-commerce.

**Step 3:** User uploads or chooses a synthetic dataset.

**Step 4:** CORVQ runs industry-specific risk analysis.

**Step 5:** The dashboard displays suspicious indicators and relationship graphs.

**Step 6:** The user starts an AI investigation.

**Step 7:** Gemini-powered agents analyse the structured evidence.

**Step 8:** ProofGuard verifies AI-generated factual claims.

**Step 9:** User can perform a counterfactual investigation by changing selected evidence.

**Step 10:** CORVQ generates a structured, evidence-backed investigation report.

**Step 11:** A human analyst reviews the findings and records a decision.

**Step 12:** The application stores the investigation history and audit records.

---

## 7. EXPECTED PROJECT STRUCTURE

```text
CORVQ/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── adapters/
│   │   │   ├── banking/
│   │   │   └── ecommerce/
│   │   ├── agents/
│   │   ├── proofguard/
│   │   ├── counterfactual/
│   │   ├── governance/
│   │   ├── llmops/
│   │   ├── database/
│   │   └── models/
│   ├── tests/
│   └── requirements.txt
│
├── datasets/
│   ├── banking/
│   └── ecommerce/
│
├── .github/
│   └── workflows/
│
├── docs/
├── README.md
├── .gitignore
├── .env.example
└── firebase.json
```

Codex can refine the structure when technically justified, but it must preserve separation between adapters, core intelligence, AI agents, evidence verification, and storage.

---

## 8. IMPLEMENTATION PHASES

### Phase 1 — Project Foundation

Create the React frontend and FastAPI backend.

Set up Git, GitHub, project configuration, tests, and SQLite.

Verify that the frontend can communicate with the backend.

### Phase 2 — Industry Adapters

Create the Banking and E-commerce adapters.

Prepare labelled synthetic datasets, validation schemas, detection rules, and evidence references.

Both adapters should return results through a shared investigation schema.

### Phase 3 — Analysis and Dashboard

Implement deterministic risk analysis, investigation APIs, and relationship graphs.

Connect the React dashboard to real backend responses.

### Phase 4 — Gemini + Google ADK

Add genuine Gemini integration and orchestrated agent workflows.

Implement structured output, error handling, evidence-grounded prompts, and agent tool restrictions.

If credentials are missing, report the integration as unconfigured rather than simulating a successful AI response.

### Phase 5 — ProofGuard

Implement independent evidence verification for factual AI claims.

Test supported, unsupported, ambiguous, and conflicting claims.

### Phase 6 — Counterfactual Analysis

Allow users to modify evidence and rerun the relevant calculations.

Show which findings change and why.

### Phase 7 — Governance

Implement human review, recorded decisions, investigation history, and audit logs.

### Phase 8 — DevSecOps + LLMOps

Set up CI tests, scanning, prompt evaluation, grounding checks, logging, and basic performance metrics.

### Phase 9 — Cloud Deployment

Once the application works locally:

- Deploy frontend to Firebase Hosting.
- Deploy backend to Google Cloud Run.
- Configure Gemini/Vertex AI.
- Connect Firestore as appropriate.
- Configure secure cloud credentials and budget safeguards.
- Test all flows using the public website.

Cloud account access and billing changes require user authorization.

### Phase 10 — Hackathon Submission

Prepare:

1. Live deployed application link.
2. Working demo video, targeting no more than 3 minutes.
3. Pitch deck using the official hackathon template, PDF under 5 MB.
4. Public GitHub repository.
5. Project description within 1,024 characters.

Follow the latest instructions on the official submission portal.

---

## 9. DEVELOPMENT RULES FOR CODEX

1. **Implement real functionality**, not a static interface pretending to perform investigations.
2. Start with a minimal working system and improve it incrementally.
3. Keep the core industry-independent.
4. Use both Banking and E-commerce as real, tested adapters.
5. Run tests after every major feature.
6. Fix errors before advancing.
7. Clearly identify implemented, incomplete, and unconfigured functionality.
8. Never hardcode secrets.
9. Use synthetic data only.
10. Require human oversight for consequential decisions.
11. Do not enable billable services without authorization.
12. Create clear documentation.
13. Maintain GitHub commits at tested milestones.
14. Prepare the application for Google Cloud deployment even while developing locally.
15. Never claim an investigation conclusion is verified unless its source evidence has been checked.

---

## 10. MVP ACCEPTANCE CRITERIA

The initial CORVQ MVP is successful when:

- React frontend runs locally.
- FastAPI backend responds correctly.
- Banking and E-commerce adapters process different synthetic datasets.
- Both use the same shared investigation engine.
- Risk indicators come from actual analysis.
- Relationship views correspond to the dataset.
- Gemini provides real, evidence-grounded investigation analysis.
- ProofGuard verifies factual claims against records.
- Counterfactual tests rerun analysis using changed evidence.
- Human review decisions can be saved and retrieved.
- Automated backend tests pass.
- Basic DevSecOps and LLMOps checks run successfully.
- Application can be deployed to Google Cloud without major architectural changes.

The hackathon submission is complete only after the live URL and all required deliverables have been verified.

---

## 11. PRODUCT DIFFERENTIATION

**CORVQ is not just an AI chatbot, fraud detector, or governance dashboard.**

Its distinctive concept is a reusable intelligence engine that investigates different industry problems while independently verifying important claims made by AI.

Our proposed signature feature is:

**ProofGuard — AI that challenges its own conclusions.**

The system should allow analysts to see:

- What the AI concluded.
- What evidence supports the claim.
- Which facts remain uncertain.
- Which claims are unsupported.
- How a conclusion changes when evidence changes.
- Who reviewed the resulting decision.

The hackathon demonstration must prove that this functionality is real and not simply present in the interface.

---

## 12. INSTRUCTIONS TO START CODING

Codex, use this specification as the source of truth for CORVQ.

Before editing files, inspect the repository and determine what already exists.

Start with **Phase 1** and work toward a fully functioning local MVP.

Build the first vertical slice:

**Select industry → Load synthetic data → Run analysis → Display real findings and evidence in React.**

After completing the first vertical slice:

- Run backend and frontend tests.
- Fix failures.
- Report the files created or modified.
- Explain how to run the application locally.
- Identify any missing configurations.
- Report which features are truly operational.

Then proceed through the remaining implementation phases.

Do not deploy or enable paid Google Cloud services without explicit approval.

**Final Mission:** Build CORVQ into a functioning, cloud-deployable, industry-adaptive AI investigation and governance platform that demonstrates trustworthy, evidence-verified intelligence across Banking and E-commerce.

**End of CORVQ Master Specification.**
