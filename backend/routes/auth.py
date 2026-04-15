from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
import uuid
import re
import httpx
import logging

from database import db
from config import PLAN_LIMITS
from models import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, ResendVerificationRequest
from auth_utils import hash_password, verify_password, create_jwt, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(data: UserRegister):
    existing = await db.users.find_one({'email': data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"

    website = data.website_url.strip()
    if website and not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    domain = ''
    if website:
        domain = re.sub(r'^https?://(www\.)?', '', website).split('/')[0].strip()

    domain_token = f"ce-verify-{uuid.uuid4().hex[:16]}"

    user_doc = {
        'user_id': user_id,
        'email': data.email,
        'password_hash': hash_password(data.password),
        'full_name': data.full_name,
        'company_name': data.company_name or '',
        'website_url': website,
        'domain': domain,
        'domain_verified': False,
        'domain_verification_token': domain_token,
        'country': 'DE',
        'marketing_consent': data.marketing_consent,
        'marketing_consent_at': datetime.now(timezone.utc).isoformat() if data.marketing_consent else None,
        'terms_accepted_at': datetime.now(timezone.utc).isoformat(),
        'plan': 'free',
        'email_verified': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user_doc)

    token = create_jwt(user_id)
    session_token = f"sess_{uuid.uuid4().hex}"
    await db.user_sessions.insert_one({
        'user_id': user_id,
        'session_token': session_token,
        'expires_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    await db.subscriptions.insert_one({
        'subscription_id': f"sub_{uuid.uuid4().hex[:12]}",
        'user_id': user_id,
        'plan': 'free',
        'messages_used_this_month': 0,
        'billing_cycle_start': datetime.now(timezone.utc).isoformat(),
        'next_reset_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    verify_token = f"verify_{uuid.uuid4().hex}"
    await db.verification_tokens.insert_one({
        'token': verify_token,
        'user_id': user_id,
        'type': 'email_verification',
        'expires_at': (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"[MOCK EMAIL] Verification email sent to {data.email} - Token: {verify_token}")

    return {
        'user_id': user_id,
        'email': data.email,
        'full_name': data.full_name,
        'plan': 'free',
        'token': token,
        'session_token': session_token,
        'email_verified': False,
        'mock_verify_token': verify_token,
        'domain': domain,
        'domain_verified': False,
        'domain_verification_token': domain_token,
    }


@router.post("/login")
async def login(data: UserLogin):
    user = await db.users.find_one({'email': data.email}, {'_id': 0})
    if not user or not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(user['user_id'])
    session_token = f"sess_{uuid.uuid4().hex}"
    await db.user_sessions.insert_one({
        'user_id': user['user_id'],
        'session_token': session_token,
        'expires_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    return {
        'user_id': user['user_id'],
        'email': user['email'],
        'full_name': user.get('full_name', ''),
        'plan': user.get('plan', 'free'),
        'company_name': user.get('company_name', ''),
        'token': token,
        'session_token': session_token,
        'email_verified': user.get('email_verified', False),
        'domain': user.get('domain', ''),
        'domain_verified': user.get('domain_verified', False),
    }


@router.post("/google-session")
async def google_session(request: Request):
    body = await request.json()
    session_id = body.get('session_id')
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    async with httpx.AsyncClient() as client_http:
        resp = await client_http.get(
            'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data',
            headers={'X-Session-ID': session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        google_data = resp.json()

    email = google_data.get('email')
    name = google_data.get('name', '')
    picture = google_data.get('picture', '')
    ext_session_token = google_data.get('session_token', '')

    user = await db.users.find_one({'email': email}, {'_id': 0})
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user = {
            'user_id': user_id,
            'email': email,
            'password_hash': '',
            'full_name': name,
            'company_name': '',
            'website_url': '',
            'domain': '',
            'domain_verified': False,
            'domain_verification_token': f"ce-verify-{uuid.uuid4().hex[:16]}",
            'country': 'DE',
            'picture': picture,
            'marketing_consent': False,
            'terms_accepted_at': datetime.now(timezone.utc).isoformat(),
            'plan': 'free',
            'email_verified': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user)
        await db.subscriptions.insert_one({
            'subscription_id': f"sub_{uuid.uuid4().hex[:12]}",
            'user_id': user_id,
            'plan': 'free',
            'messages_used_this_month': 0,
            'billing_cycle_start': datetime.now(timezone.utc).isoformat(),
            'next_reset_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
    else:
        user_id = user['user_id']
        await db.users.update_one({'user_id': user_id}, {'$set': {'full_name': name, 'picture': picture, 'updated_at': datetime.now(timezone.utc).isoformat()}})

    session_token = ext_session_token or f"sess_{uuid.uuid4().hex}"
    await db.user_sessions.insert_one({
        'user_id': user_id,
        'session_token': session_token,
        'expires_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    return {
        'user_id': user_id,
        'email': email,
        'full_name': name,
        'plan': user.get('plan', 'free'),
        'company_name': user.get('company_name', ''),
        'session_token': session_token,
    }


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    return {
        'user_id': user['user_id'],
        'email': user['email'],
        'full_name': user.get('full_name', ''),
        'company_name': user.get('company_name', ''),
        'plan': user.get('plan', 'free'),
        'picture': user.get('picture', ''),
        'marketing_consent': user.get('marketing_consent', False),
        'created_at': user.get('created_at', ''),
        'email_verified': user.get('email_verified', False),
        'website_url': user.get('website_url', ''),
        'domain': user.get('domain', ''),
        'domain_verified': user.get('domain_verified', False),
        'domain_verification_token': user.get('domain_verification_token', ''),
    }


@router.post("/logout")
async def logout(request: Request):
    session_token = request.cookies.get('session_token')
    if session_token:
        await db.user_sessions.delete_one({'session_token': session_token})
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        await db.user_sessions.delete_one({'session_token': token})
    return {"ok": True}


# ---------- EMAIL VERIFICATION ----------
@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    token_doc = await db.verification_tokens.find_one({'token': data.token, 'type': 'email_verification'}, {'_id': 0})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    expires_at = token_doc.get('expires_at', '')
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification token has expired")
    await db.users.update_one({'user_id': token_doc['user_id']}, {'$set': {'email_verified': True, 'updated_at': datetime.now(timezone.utc).isoformat()}})
    await db.verification_tokens.delete_one({'token': data.token})
    return {"ok": True, "message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest):
    user = await db.users.find_one({'email': data.email}, {'_id': 0})
    if not user:
        return {"ok": True, "message": "If an account exists, a verification email has been sent."}
    if user.get('email_verified'):
        return {"ok": True, "message": "Email already verified."}
    await db.verification_tokens.delete_many({'user_id': user['user_id'], 'type': 'email_verification'})
    verify_token = f"verify_{uuid.uuid4().hex}"
    await db.verification_tokens.insert_one({
        'token': verify_token,
        'user_id': user['user_id'],
        'type': 'email_verification',
        'expires_at': (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"[MOCK EMAIL] Verification link: /verify-email?token={verify_token}")
    return {"ok": True, "message": "Verification email sent.", "mock_token": verify_token}


# ---------- PASSWORD RESET ----------
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await db.users.find_one({'email': data.email}, {'_id': 0})
    if not user:
        return {"ok": True, "message": "If an account with that email exists, a reset link has been sent."}
    if not user.get('password_hash'):
        return {"ok": True, "message": "This account uses Google login. Please sign in with Google."}
    await db.verification_tokens.delete_many({'user_id': user['user_id'], 'type': 'password_reset'})
    reset_token = f"reset_{uuid.uuid4().hex}"
    await db.verification_tokens.insert_one({
        'token': reset_token,
        'user_id': user['user_id'],
        'type': 'password_reset',
        'expires_at': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"[MOCK EMAIL] Password reset link: /reset-password?token={reset_token}")
    return {"ok": True, "message": "If an account with that email exists, a reset link has been sent.", "mock_token": reset_token}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    token_doc = await db.verification_tokens.find_one({'token': data.token, 'type': 'password_reset'}, {'_id': 0})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    expires_at = token_doc.get('expires_at', '')
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    new_hash = hash_password(data.new_password)
    await db.users.update_one({'user_id': token_doc['user_id']}, {'$set': {'password_hash': new_hash, 'updated_at': datetime.now(timezone.utc).isoformat()}})
    await db.verification_tokens.delete_one({'token': data.token})
    await db.user_sessions.delete_many({'user_id': token_doc['user_id']})
    return {"ok": True, "message": "Password reset successfully. Please login with your new password."}
