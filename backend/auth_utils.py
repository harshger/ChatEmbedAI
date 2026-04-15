import hashlib
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from fastapi import Request, HTTPException
from database import db
from config import JWT_SECRET


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_jwt(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


async def get_current_user(request: Request):
    session_token = request.cookies.get('session_token')
    if session_token:
        session = await db.user_sessions.find_one({'session_token': session_token}, {'_id': 0})
        if session:
            expires_at = session.get('expires_at')
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at > datetime.now(timezone.utc):
                user = await db.users.find_one({'user_id': session['user_id']}, {'_id': 0})
                if user:
                    return user

    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        session = await db.user_sessions.find_one({'session_token': token}, {'_id': 0})
        if session:
            expires_at = session.get('expires_at')
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at > datetime.now(timezone.utc):
                user = await db.users.find_one({'user_id': session['user_id']}, {'_id': 0})
                if user:
                    return user
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = await db.users.find_one({'user_id': payload['user_id']}, {'_id': 0})
            if user:
                return user
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

    raise HTTPException(status_code=401, detail="Not authenticated")
