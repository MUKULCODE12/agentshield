from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Policy, User, AuditLog
from app.schemas.schemas import PolicyCreate, PolicyOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[PolicyOut])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Policy).filter(Policy.org_id == current_user.org_id).all()

@router.post("", response_model=PolicyOut)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    policy = Policy(
        org_id=current_user.org_id,
        title=policy_in.title,
        category=policy_in.category,
        description=policy_in.description,
        rule_type=policy_in.rule_type,
        content=policy_in.content,
        action_on_trigger=policy_in.action_on_trigger,
        risk_score_weight=policy_in.risk_score_weight,
        is_active=policy_in.is_active,
        version=1
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="CREATE_POLICY",
        resource_type="Policy",
        resource_id=str(policy.id),
        details={"title": policy.title, "action": policy.action_on_trigger}
    )
    db.add(audit)
    db.commit()

    return policy

@router.put("/{policy_id}/toggle")
def toggle_policy(policy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    policy = db.query(Policy).filter(Policy.id == policy_id, Policy.org_id == current_user.org_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy.is_active = not policy.is_active
    db.commit()

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="TOGGLE_POLICY",
        resource_type="Policy",
        resource_id=str(policy.id),
        details={"is_active": policy.is_active}
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "policy_id": policy.id, "is_active": policy.is_active}
