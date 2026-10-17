# Verification

Local verification completed on 2026-10-17:

- 17 backend regression tests pass.
- Frontend graph mapping unit test passes.
- Vite production build succeeds.
- Browser: banking sample produces 8 evidence records, 7 entities and 5 risk findings.
- Browser: ProofGuard rejects TX-001 amount 50000 with actual evidence value 145000.
- Browser: removing TX-003 creates a separate 7-record scenario with 3 findings; original remains in history.
- Browser: e-commerce sample produces 8 records, 8 entities and 2 findings (refund cluster and repeated orders).

Live Gemini, cloud deployment and GitHub security workflows have not been executed. CI configuration is supplied but requires a repository remote. Production identity, Firestore and immutable auditing remain future work.

![Workspace preview](workspace-preview.png)

## Live Gemini validation

A live synthetic banking investigation completed successfully with Gemini 3.8 Flash through the four-agent ADK workflow. It produced 24 structured atomic claims; all 24 matched source records in ProofGuard, with zero unsupported claims in this run. Latency was approximately 83 seconds. This single scenario does not establish general model accuracy. Broad narrative statements remain unverified.

The previous default, Gemini 2.5 Flash, returned an API response stating it was unavailable to new users and recommending Gemini 3.8 Flash. The local default was updated accordingly. API quota and billing depend on the configured Google project.
