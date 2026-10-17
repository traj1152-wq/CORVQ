# Architecture and implementation status

`backend/app/models.py` defines the shared validated record, claim and API contracts.
`adapters/` owns domain-specific rules and kind validation. `core/` coordinates adapters and builds a shared graph/result. `proofguard/` independently checks atomic factual claims. `agents/` contains optional Gemini/ADK orchestration. `database/` contains the repository protocol and SQLite implementation. `main.py` exposes REST endpoints, review operations, recalculated scenarios and report export.

The React workspace displays real API results; it never supplies fabricated investigation outputs. React Flow renders the API graph. Samples are clearly synthetic. Counterfactual findings are recalculated, and each scenario gets a new investigation ID with a parent reference. A finding signature is its rule and evidence IDs: replacement amounts can alter explanation text without counting as a new finding if its rule and evidence set are unchanged.

## Limits and next milestones

- Add explicit industry-native ingestion schemas and CSV import; current records use a common source/target contract with industry-specific kind checks.
- Introduce supplied policy documents and source citations; current policy agent has no regulatory knowledge corpus.
- Run a live Gemini integration evaluation once API access is authorized. Structured atomic facts are verified; broad narratives and hypotheses remain unverified.
- Add Firestore implementation, transactional investigation/review updates and production identity with reviewer roles.
- Append-only audit API currently persists in mutable SQLite; production needs independent integrity controls.
- Add rate limits, request-body size enforcement, durable storage and token rotation before internet exposure.
- Add React interaction/browser tests beyond graph mapping. Extend known-scenario evaluations and prompt regression tests with real Gemini responses.
- Cloud deployment and hackathon deliverables require their own verified milestones.

This code intentionally performs no account enforcement and no seller enforcement. Rule thresholds are synthetic demonstration settings. Cycle enumeration is bounded to length four and 100 returned cycles; it is not exhaustive fraud detection.

## Identity and storage update

Firebase identity validation, server role checks, workspace isolation and verified reviewer identity are now implemented. Firestore persistence and optimistic revision checks are implemented. Both repositories now reject stale saves. See production-setup.md for actual configuration requirements and verification limits; earlier milestone notes above describe the initial MVP.
