import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    """Computes a salted SHA-256 password hash."""
    salt = "agentshield_salt_2026"
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    return hash_password(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_agent_api_key(prefix: str = "sk_live_") -> tuple[str, str]:
    """
    Generates a secure API Key and its SHA-256 hash.
    Returns (raw_key, key_hash)
    """
    raw_secret = secrets.token_hex(24)
    api_key = f"{prefix}{raw_secret}"
    key_hash = hash_api_key(api_key)
    return api_key, key_hash

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
