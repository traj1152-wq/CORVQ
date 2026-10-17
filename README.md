# CORVQ

**One Intelligence Engine. Every Industry.**

A local investigation workspace built with React, Vite, Tailwind, React Flow, FastAPI, Pydantic, NetworkX, and SQLite. All included scenarios are explicitly synthetic.

## Run locally

Use Python 3.11+ (3.12 recommended for optional ADK compatibility), Node.js 20.19+ and pnpm 10+.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd frontend
pnpm install
pnpm dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend. API documentation: http://127.0.0.1:8000/docs. If pnpm reports blocked esbuild scripts, allow only `esbuild` with `pnpm approve-builds`.

On this machine Node and pnpm are bundled with Codex rather than on PATH. `start-local.ps1` uses the detected bundled runtime when necessary. Run `./start-local.ps1 backend` and `./start-local.ps1 frontend` in two terminals.

## Operational features

- Banking and e-commerce adapters use the same validated investigation pipeline.
- Banking: high-value transfers and directed cycles of 2–4 accounts (up to 100 cycles).
- E-commerce: at least three refunds from a seller or three orders from a buyer to one seller within the supplied dataset.
- Evidence IDs, graph edges, amounts, and rule findings derive from submitted records.
- ProofGuard verifies atomic amount, source, target, and kind claims by exact comparison. It distinguishes verified, unsupported and needs-review claims. It does **not** verify an entire free-text narrative.
- Counterfactuals remove records through the UI; the API also supports replacement records. All rules and graph relationships are recalculated, preserving the original investigation.
- SQLite stores history, claim results, analyst decisions and audit events.
- Downloadable JSON reports contain source evidence, findings, verification results, review decisions and audit events.
- Gemini configuration is reported explicitly; missing credentials never produce simulated AI reports.

## Demo

1. Choose Banking; click **Load sample & analyze**.
2. Explore the relationship map and findings. Open Evidence to see records.
3. Open ProofGuard. Assert TX-001 has amount 145000, then 50000. The first verifies; the second conflicts with the actual amount.
4. In Counterfactual, remove TX-003. The ACC-1042 / ACC-2087 / ACC-3091 cycle disappears. The separate unrelated cycle remains.
5. Record a human review and inspect Audit trail. Export the report.
6. Switch to E-commerce and load its sample. Removing REF-003 resolves the refund-cluster finding while repeated orders remain.

## Synthetic uploads

Upload a JSON array or an object with a `records` array. Select the corresponding industry first. Included files live in `datasets/`.

```json
[{"id":"TX-001","source":"ACC-A","target":"ACC-B","amount":145000,"timestamp":"2026-10-17T09:00:00Z","kind":"transfer"}]
```

Amounts are INR. Banking accepts `transfer`; e-commerce accepts `purchase` and `refund`. Refund direction is seller to buyer. IDs must be unique, amounts positive and timestamps ISO formatted. The record limit is 5,000. Upload synthetic data only. Thresholds are demonstration rules, not regulatory or fraud determinations.

## Optional Gemini + Google ADK

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-ai.txt
$env:GEMINI_API_KEY = 'your-key'
$env:GEMINI_MODEL = 'gemini-2.5-flash'
```

Restart the backend. Environment variables are read from the process; `.env.example` is a reference, not automatically loaded. Agents use a read-only backend evidence tool. ADK SequentialAgent coordinates investigation, relationship, policy and report agents. Pydantic validates the report; ProofGuard checks its structured atomic claims. No policy documents are included, and the policy agent must state that limitation. Model and prompt versions, latency, available token usage and errors are recorded. Cost is unavailable rather than estimated.

**Live Gemini execution is unverified until authorized credentials and the optional ADK dependencies are configured. Calling Gemini can incur charges.** No billable services were enabled by this project setup.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
pnpm test
pnpm build
```

Tests cover both adapters, counterfactual recalculation, factual verification, validation, persistence, review, audit, API authentication and unconfigured AI behavior. Frontend unit tests cover graph evidence mapping; production build validates the component bundle. CI additionally runs Semgrep, pip-audit, secret scanning and Trivy. CI scanners must still be verified in GitHub.

## Security and deployment status

Development defaults to loopback and no authentication. Set `CORVQ_API_TOKEN` for authenticated API access; the UI's Access settings stores it in sessionStorage. This is a shared development token, not production identity or RBAC. Analyst names are self-reported. Cloud Run fails closed if no API token is configured.

A repository protocol isolates SQLite for a future Firestore implementation. **Firestore, user identities/RBAC, tamper-resistant audit storage, rate limiting, distributed transactions, authenticated human identities, production evaluation, and hosted deployment are not implemented.** Current audit storage is suitable for a local MVP, not regulated production. Concurrent review updates can overwrite each other; use one analyst at a time.

The Dockerfile and Firebase configuration prepare deployment without enabling services. Supply a Firebase project and a backend route before deploying. Use authenticated Cloud Run access, Secret Manager, configured CORS, durable storage and budget controls. SQLite inside Cloud Run is ephemeral and must be replaced before a durable hosted deployment. No public GitHub remote, cloud resources or hackathon deliverables have been created.

See `docs/architecture.md` for module boundaries and next steps.
