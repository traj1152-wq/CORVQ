"""Prepare or apply a role assignment with trusted administrator credentials.

Default is a dry run. Run --apply only after approving the displayed assignment.
"""
import argparse
import json
import re
parser=argparse.ArgumentParser()
parser.add_argument('--project',required=True)
parser.add_argument('--uid',required=True)
parser.add_argument('--workspace',required=True)
parser.add_argument('--role',choices=['viewer','analyst','reviewer','admin'],required=True)
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',args.workspace):parser.error('Invalid workspace identifier')
plan={'project':args.project,'uid':args.uid,'role':args.role,'workspace':args.workspace,'apply':args.apply}
print(json.dumps(plan))
if args.apply:
    import firebase_admin
    from firebase_admin import auth
    app=firebase_admin.initialize_app(options={'projectId':args.project})
    user=auth.get_user(args.uid,app=app)
    if not user.email_verified:raise SystemExit('User must verify their email first')
    claims={**(user.custom_claims or {}),'corvq_role':args.role,'corvq_workspace':args.workspace}
    auth.set_custom_user_claims(args.uid,claims,app=app)
    # Invalidate prior refresh sessions so previous role permissions cannot persist.
    auth.revoke_refresh_tokens(args.uid,app=app)
    print('Role assigned. User must sign in again.')
else:
    print('Dry run only. No Google API calls were made.')
