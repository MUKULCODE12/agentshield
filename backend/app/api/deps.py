from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.config import settings
from app.db.models import User, Agent, Organization
from app.core.security import hash_api_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    return user
        except Exception:
            pass

    # Fallback to first user in DB for demo / unauthenticated API access
    user = db.query(User).first()
    if user:
        return user

    # Auto-provision default Demo Admin user if DB is fresh
    org = db.query(Organization).first()
    if not org:
        org = Organization(name="Acme Corp Enterprise", slug="acme-corp", plan="Enterprise")
        db.add(org)
        db.commit()
        db.refresh(org)

    user = User(
        org_id=org.id,
        email="admin@agentshield.com",
        hashed_password="admin_hashed_demo",
        full_name="Security Admin",
        role="Admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_agent_from_header_or_body(
    x_agent_api_key: Optional[str] = Header(None, alias="X-Agent-API-Key"),
    db: Session = Depends(get_db)
) -> Optional[Agent]:
    if x_agent_api_key:
        key_hash = hash_api_key(x_agent_api_key)
        return db.query(Agent).filter(Agent.api_key_hash == key_hash).first()
    return None
