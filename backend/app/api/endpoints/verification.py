from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import VerificationRecord, User
from app.schemas.schemas import VerificationOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[VerificationOut])
def list_verifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(VerificationRecord).filter(
        VerificationRecord.org_id == current_user.org_id
    ).order_by(VerificationRecord.verified_at.desc()).all()
    return records
