# Production access and persistence

Backend configuration (local `.env`, process environment or cloud secrets):

```
CORVQ_AUTH_MODE=firebase
CORVQ_STORAGE=firestore
CORVQ_FIREBASE_PROJECT=your-project-id
```

Install `backend/requirements-cloud.txt`. Use Application Default Credentials locally; on Cloud Run use a dedicated service identity with only the required Firebase Authentication lookup/revocation-check and Firestore access. Do not store service-account keys in the repository. Cloud Run rejects local/token authentication or SQLite storage. No cloud project, billing, authentication provider or Firestore database is created by this code.

Firebase Admin validates ID-token signature, expiry, issuer, audience and revocation/disabled-user state. Verified email is required. A trusted administrator assigns these custom claims through the Firebase Admin SDK:

```
{"corvq_role":"analyst","corvq_workspace":"team-one"}
```

Supported roles: `viewer` reads workspace cases, reports and history; `analyst` creates investigations, verifies claims, runs AI and creates counterfactuals; `reviewer` records human decisions; `admin` has all application permissions. The UI cannot assign claims. Sign out and back in after claim changes. No self-registration or role-assignment HTTP endpoint is provided.

For frontend email/password sign-in, enable that provider and create/verify accounts in your Firebase project. Add the public Firebase web API key to `frontend/.env` as `VITE_FIREBASE_API_KEY=...`, then restart/rebuild Vite. This is not the Gemini key. The browser signs in directly with Firebase and keeps ID/refresh tokens in memory; page reloads require sign-in again. Use Access settings to sign in or sign out. REST APIs: https://firebase.google.com/docs/reference/rest/auth

Every Firebase user is scoped to their assigned workspace. Firestore data lives under `workspaces/{workspace}/investigations/{id}`. Direct browser Firestore access is denied by `firestore.rules`; server IAM governs Admin SDK access. Deploy those rules explicitly after cloud authorization. In local Firebase+SQLite testing, workspaces get separate hashed database filenames.

Both repositories reject stale saves using revisions, returning HTTP 409 instead of overwriting a concurrent update. Firestore uses transactions and stores investigation bodies as serialized JSON to preserve nested graph/result structures. A conservative 850 KB body limit returns HTTP 413; split larger datasets. SQLite retains local data; Firestore supplies durable hosted storage once configured. Existing SQLite cases are not migrated automatically.

Reviews in Firebase mode derive analyst identity from the verified principal, ignoring the supplied analyst name. Local mode remains a clearly labelled development bypass. API-token mode is development-only.

## Verification limits and deployment requirements

Offline tests mock the verified Firebase identity boundary; they do not prove live token acceptance or revocation. Firestore repository contract tests use an in-memory client double. Live Firebase/Firestore verification, actual IAM permissions, a Firestore emulator run, browser sign-in with real accounts, and deployment remain pending external setup. No paid services were enabled.

Audit documents are append-only through this API but are mutable by privileged cloud operators. Case save and audit append are separate operations, so cross-document atomic auditing is not guaranteed. Multi-tenant storage is isolated at the server workspace boundary; this is not a formal security certification. Rate limits, strict HTTP payload limits, account provisioning, MFA policy, immutable archival and production rollout checks are still needed.

Cloud image: `docker build --build-arg INSTALL_CLOUD=true --build-arg INSTALL_AI=true -t corvq .`

## Request safeguards

The API now enforces a 2 MiB maximum request body, including chunked requests. Defaults: 120 API requests per minute per direct peer IP and 5 AI requests per minute. Limits return HTTP 429 with Retry-After; oversized uploads return 413. Configure CORVQ_MAX_REQUEST_BYTES, CORVQ_REQUESTS_PER_MINUTE and CORVQ_AI_REQUESTS_PER_MINUTE as needed.

These counters are process-local, so aggregate quotas across Cloud Run instances require a gateway or shared limiter. Proxy peers may share a bucket. Untrusted forwarded-IP headers cannot bypass limits. The API adds no-store, no-referrer and nosniff response headers. Cloud budgets and provider quotas must still be configured before deployment.

Run `python scripts/check_readiness.py` for a read-only configuration report. It prints only presence checks, never keys. It does not validate billing, IAM or live connectivity. `scripts/admin_access.py` prepares an explicit role/workspace assignment and makes no API calls unless --apply is supplied. Each actual permission grant must be approved; use trusted administrator credentials and never put those credentials in the repository.

## Deployment sequence (requires project and authorization)

1. Create/select the CORVQ Firebase project without enabling billing. Record the project ID.
2. Register a web app; save only its public Firebase web API key in frontend/.env.
3. Enable the email/password provider and create verified analyst/reviewer accounts. Assign approved custom claims using the dry-run-first admin helper.
4. Select a Firestore location deliberately before creating the database. Keep direct browser access denied. Configure server Application Default Credentials for local live tests.
5. Validate user sign-in, reviewer restrictions, workspace separation, durable save/reload and token revocation against the live project.
6. Review Cloud Run/Firebase billing requirements and approve budget, APIs, service identity/IAM and deployment. No billing or permission changes happen automatically.
7. Build the cloud image with INSTALL_CLOUD=true and INSTALL_AI=true. Supply GEMINI_API_KEY from Secret Manager, CORVQ_AUTH_MODE=firebase, CORVQ_STORAGE=firestore and CORVQ_FIREBASE_PROJECT. Configure frontend origin and conservative scaling.
8. Deploy backend service corvq-api in the region in firebase.json; deploy frontend hosting and firestore.rules. Test the public URL before marking submission complete.

No CLI provisioning commands have been run yet. Cloud account state, required billing tier, quotas, costs and IAM must be checked against the selected project at deployment time.

## Live Firebase setup — 2026-10-17

- Firebase project: corvq-493d5 (CORVQ), Spark plan.
- Web app: CORVQ Web, registered. Public web API configuration is stored in ignored frontend/.env.
- Email/password provider: enabled; passwordless sign-in remains off.
- Default Firestore database: created in asia-south1 (Mumbai), production mode denying direct client reads/writes.
- Paid backup schedules and billing upgrades: not enabled.
- Actual user provisioning, approved role grants, server Application Default Credentials, live sign-in/revocation validation and backend durable writes: pending.
- Local backend remains in development/SQLite mode until credentials and real account access are validated; the live Firestore database being present does not mean app persistence has switched.

Email verification can be requested from CORVQ Access settings using Verify Firebase email. The account owner enters their password locally; Firebase receives credentials directly, sends its verification email, and the temporary sign-in session is discarded. Do not send passwords or verification links through chat. Role assignment remains blocked by the admin helper until Firebase reports email_verified=true.
