from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Approval, User, Agent
from app.schemas.schemas import ApprovalOut, ApprovalAction
from app.engine.approval import process_approval_decision
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[ApprovalOut])
def list_approvals(status_filter: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Approval).filter(Approval.org_id == current_user.org_id)
    if status_filter:
        query = query.filter(Approval.status == status_filter.upper())
    
    approvals = query.order_by(Approval.requested_at.desc()).all()

    results = []
    for app in approvals:
        agent = db.query(Agent).filter(Agent.id == app.agent_id).first()
        agent_name = agent.name if agent else "Unknown Agent"
        results.append(ApprovalOut(
            id=app.id,
            org_id=app.org_id,
            execution_id=app.execution_id,
            agent_id=app.agent_id,
            agent_name=agent_name,
            tool_name=app.tool_name,
            tool_input=app.tool_input or {},
            risk_score=app.risk_score,
            status=app.status,
            requested_at=app.requested_at,
            responded_at=app.responded_at,
            approved_by=app.approved_by,
            rejection_reason=app.rejection_reason
        ))
    return results

@router.post("/{approval_id}/action")
def respond_approval(
    approval_id: int,
    action_in: ApprovalAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        res = process_approval_decision(
            db=db,
            approval_id=approval_id,
            action=action_in.action,
            user_email=current_user.email,
            reason=action_in.reason
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
