import jwt
from datetime import datetime, timedelta
import bcrypt
from .config import settings

def hash_password(pw: str):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw.encode('utf-8'), salt).decode('utf-8')

def verify_password(raw: str, hashed: str):
    """Verify password against hash using bcrypt"""
    if not hashed:
        return False
    
    try:
        # Use bcrypt directly (more reliable than passlib)
        return bcrypt.checkpw(raw.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}, hash: {hashed[:30]}...")
        return False

def create_jwt_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": email, "exp": expire}

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None