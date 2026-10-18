# CORVQ

**One Intelligence Engine. Every Industry.**

A local investigation workspace built with React, Vite, Tailwind, React Flow, FastAPI, Pydantic, NetworkX, and SQLite. All included scenarios are explicitly synthetic.

## Live prototype

Open **https://corvq-493d5.web.app**. Load a synthetic sample, then click
**Generate Gemini report**. The hosted prototype uses Firebase AI Logic with
App Check protection and checks atomic report claims against source records.
Cases and reports stay in browser memory and reset on reload. Uploads and
counterfactual recalculation require the full backend.

The Firebase project remains on Spark with billing disabled. Free model quotas
can interrupt availability. See [the free prototype setup](docs/free-prototype.md)
for architecture, validation evidence and deployment details.

Build the hosted version with `cd frontend` followed by `pnpm install --frozen-lockfile`
and `pnpm build:showcase`. The default build and local setup below use FastAPI.

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
$env:GEMINI_MODEL = 'gemini-3.8-flash'
```

Restart the backend. The backend loads the root `.env` file automatically without overriding existing process environment variables. `.env.example` documents the supported settings. Never commit `.env`. Agents use a read-only backend evidence tool. ADK SequentialAgent coordinates investigation, relationship, policy and report agents. Pydantic validates the report; ProofGuard checks its structured atomic claims. No policy documents are included, and the policy agent must state that limitation. Model and prompt versions, latency, available token usage and errors are recorded. Cost is unavailable rather than estimated.

The public prototype's single-request Firebase AI Logic workflow has been verified live. The separate four-agent backend workflow still requires validation with the chosen credentials and quotas. Keep the hosted project unlinked from billing for the free-tier prototype.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
pnpm test
pnpm build
```

Tests cover both adapters, counterfactual recalculation, factual verification, validation, persistence, review, audit, API authentication and unconfigured AI behavior. Frontend unit tests cover graph evidence mapping; production build validates the component bundle. CI additionally runs Semgrep, pip-audit, secret scanning and Trivy. CI scanners must still be verified in GitHub.

## Security and deployment status

Development defaults to loopback and no authentication. Set `CORVQ_API_TOKEN` for authenticated API access; the UI's Access settings stores it in sessionStorage. This is a shared development token, not production identity or RBAC. Analyst names are self-reported. Cloud Run fails closed unless Firebase authentication and Firestore storage are selected.

A repository protocol supports SQLite and an explicitly selected Firestore implementation. See [production setup](docs/production-setup.md). Firebase identity and scoped Firestore persistence have been exercised locally against the configured cloud project. The public prototype uses session memory instead. Tamper-resistant audit storage, cross-document atomic auditing, production evaluation and full backend deployment remain incomplete. Process-local request limits are implemented. Current audit storage is suitable for a local MVP, not regulated production. Revision checks reject conflicting concurrent updates with HTTP 409.

The Dockerfile and default Firebase configuration prepare the full backend deployment. Supply a backend route before using that Firebase configuration. Use Firebase user authorization, managed secrets, configured CORS, durable storage and cost controls. SQLite is rejected on Cloud Run. The public prototype uses a separate static-only Hosting release through `scripts/deploy_showcase.py`, which refuses projects with billing enabled. The public source repository is https://github.com/traj1152-wq/CORVQ.

See `docs/architecture.md` for module boundaries and next steps.


