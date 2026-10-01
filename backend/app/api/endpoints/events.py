from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SecurityEvent, User
from app.schemas.schemas import SecurityEventOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[SecurityEventOut])
def list_security_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = db.query(SecurityEvent).filter(
        SecurityEvent.org_id == current_user.org_id
    ).order_by(SecurityEvent.created_at.desc()).all()
    return events
