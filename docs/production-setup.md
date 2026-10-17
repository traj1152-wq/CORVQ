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
