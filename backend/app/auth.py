"""Firebase identity verification and server-enforced workspace roles."""
import os
import re
import secrets
from dataclasses import dataclass
from functools import lru_cache
from fastapi import Depends, Header, HTTPException

@dataclass(frozen=True)
class Principal:
    uid: str
    name: str
    role: str
    workspace: str
    mode: str


def auth_mode():
    return os.getenv('CORVQ_AUTH_MODE', 'token' if os.getenv('CORVQ_API_TOKEN') else 'local')

@lru_cache(maxsize=4)
def firebase_app(project):
    import firebase_admin
    return firebase_admin.initialize_app(options={'projectId':project}, name='corvq-'+project)

def verify_firebase_token(token):
    from firebase_admin import auth
    project=os.getenv('CORVQ_FIREBASE_PROJECT')
    if not project:
        raise HTTPException(503, 'Firebase project is not configured')
    return auth.verify_id_token(token, app=firebase_app(project), check_revoked=True)

def authorize(authorization: str | None = Header(default=None)):
    mode=auth_mode()
    if os.getenv('K_SERVICE') and (mode!='firebase' or os.getenv('CORVQ_STORAGE')!='firestore'):
        raise HTTPException(503, 'Cloud deployment requires Firebase authentication and Firestore storage')
    if mode=='local':
        return Principal('local-analyst','Local analyst','admin','local','local')
    token=(authorization or '').removeprefix('Bearer ')
    if not authorization or not authorization.startswith('Bearer ') or not token:
        raise HTTPException(401,'Sign in to continue',headers={'WWW-Authenticate':'Bearer'})
    if mode=='token':
        expected=os.getenv('CORVQ_API_TOKEN','')
        if not expected or not secrets.compare_digest(token,expected):
            raise HTTPException(401,'Invalid API token')
        return Principal('development-token','Development analyst','admin','local','token')
    if mode!='firebase':
        raise HTTPException(503,'Unsupported authentication configuration')
    try:
        claims=verify_firebase_token(token)
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(503,'Install backend/requirements-cloud.txt')
    except Exception:
        raise HTTPException(401,'Session invalid, expired, revoked or user disabled',headers={'WWW-Authenticate':'Bearer'})
    role=claims.get('corvq_role')
    workspace=claims.get('corvq_workspace','')
    if role not in {'viewer','analyst','reviewer','admin'} or not isinstance(workspace,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',workspace):
        raise HTTPException(403,'An administrator must assign your CORVQ role and workspace')
    if not claims.get('uid') or claims.get('email_verified') is not True:
        raise HTTPException(403,'A verified email identity is required')
    return Principal(claims['uid'],claims.get('email',claims['uid']),role,workspace,mode)

def require(*roles):
    def permitted(principal: Principal = Depends(authorize)):
        if principal.role not in roles and principal.role!='admin':
            raise HTTPException(403,'Your role cannot perform this action')
        return principal
    return permitted

analyst=require('analyst')
reviewer=require('reviewer')
