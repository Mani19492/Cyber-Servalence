import base64
import numpy as np
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from .config import settings
from .db import get_user_by_email

# ----------------- Embedding Encryption ----------------- #

fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_embedding(vec: np.ndarray) -> str:
    raw = vec.astype("float32").tobytes()
    token = fernet.encrypt(raw)
    return base64.b64encode(token).decode()

def decrypt_embedding(b64: str) -> np.ndarray:
    token = base64.b64decode(b64.encode())
    raw = fernet.decrypt(token)
    return np.frombuffer(raw, dtype="float32")

def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return 1 - float(np.dot(a, b))

# ----------------- Password Hashing ----------------- #

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ----------------- JWT Auth ----------------- #

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: int = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or settings.JWT_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str = payload.get("sub")
        if email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = get_user_by_email(email)
    if not user:
        raise cred_exc
    return user

def require_role(role: str):
    async def _role_dep(current_user=Depends(get_current_user)):
        if current_user.get("role") not in [role, "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return _role_dep
