"""Read-only deployment configuration check. Never prints credential values."""
import importlib.util
import json
import os
from pathlib import Path
from dotenv import load_dotenv

root=Path(__file__).resolve().parents[1]
load_dotenv(root/'.env',override=False)

def installed(module):
    try:return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:return False

frontend=root/'frontend'/'.env'
web_key=False
if frontend.exists():
    from dotenv import dotenv_values
    web_key=bool(dotenv_values(frontend).get('VITE_FIREBASE_API_KEY'))
checks={
    'firebase_auth_selected':os.getenv('CORVQ_AUTH_MODE')=='firebase',
    'firestore_selected':os.getenv('CORVQ_STORAGE')=='firestore',
    'firebase_project_configured':bool(os.getenv('CORVQ_FIREBASE_PROJECT')),
    'firebase_admin_installed':installed('firebase_admin'),
    'firestore_client_installed':installed('google.cloud.firestore'),
    'frontend_firebase_configured':web_key,
    'gemini_key_present':bool(os.getenv('GEMINI_API_KEY')),
    'adk_installed':installed('google.adk'),
    'frontend_build_present':(root/'frontend'/'dist'/'index.html').exists(),
}
print(json.dumps({'configuration_checks':checks,'ready_for_live_validation':all(checks.values()),
    'note':'Configuration checks only. IAM, billing, real user sign-in, token revocation and durable writes still require live verification.'},indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
