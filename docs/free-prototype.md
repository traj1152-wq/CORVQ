# Free hosted prototype

The Firebase Hosting prototype supports the included synthetic banking and
e-commerce scenarios. Cases, reviews, and reports stay in browser memory and
reset on reload. Uploads and counterfactual recalculation require the backend.

Run `pnpm build:showcase` in `frontend/` to build the hosted Gemini workflow.
Alternatively set `VITE_SHOWCASE=true` and `VITE_SHOWCASE_AI=true` when building.
The default full application build still uses FastAPI.

The hosted workflow uses the official Firebase AI Logic Web SDK, the Gemini
Developer API, and a production App Check provider restricted to the two CORVQ
Firebase Hosting domains. Firebase AI Logic App Check enforcement is enabled.
No private Gemini API key belongs in browser code. `firebase-public.json`
contains only Firebase web configuration and the public attestation site key.

One request asks Gemini for an evidence-grounded structured report. A strict
validator checks the output before saving it to session memory. Every atomic
claim is compared against the supplied source record, ignoring verification
labels supplied by the model. Unknown evidence requires review. Summaries and
hypotheses are not certified by these field comparisons. Reports can be exported
as JSON with model/prompt versions, token usage when available, and audit events.

Only synthetic fixtures are sent to Gemini. No policies are supplied, and the
prompt requires this limitation to be acknowledged. The browser prevents
concurrent reports and has a 30-second cooldown as a convenience, not a security
or distributed quota control. Provider quotas and App Check govern public use.
Quota or provider errors do not produce a simulated or saved AI report.

Keep project `corvq-493d5` unlinked from billing on Spark to use the Gemini
Developer API free tier. Free quota exhaustion can interrupt AI availability.
Do not link billing or upgrade services as part of showcase deployment.

## Live verification, 18 October 2026

The public Firebase Hosting site completed a Gemini 3.8 Flash banking report in
the browser. All four returned atomic claims matched source evidence. The audit
record reported one request, 28,008 ms total latency including client setup, and
1,464 total tokens. This is one functional smoke test, not a performance or
accuracy benchmark. The production build and four frontend tests passed. A scan
confirmed the private backend Gemini key is absent from public JavaScript.
App Check registration and AI Logic enforcement were confirmed in the console.
Project billing was checked again and remained disabled with no linked account.

References:
- https://firebase.google.com/docs/ai-logic/get-started?platform=web
- https://firebase.google.com/docs/ai-logic/pricing
- https://firebase.google.com/docs/ai-logic/app-check
- https://docs.cloud.google.com/recaptcha/docs/billing-information
