from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Agent, Tool, Execution, Approval, VerificationRecord, SecurityEvent, User
from app.schemas.schemas import DashboardStats
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/overview", response_model=DashboardStats)
def get_dashboard_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = current_user.org_id

    total_agents = db.query(Agent).filter(Agent.org_id == org_id).count()
    total_tools = db.query(Tool).filter(Tool.org_id == org_id).count()
    total_executions = db.query(Execution).filter(Execution.org_id == org_id).count()

    allowed_count = db.query(Execution).filter(Execution.org_id == org_id, Execution.decision == "ALLOW").count()
    blocked_count = db.query(Execution).filter(Execution.org_id == org_id, Execution.decision == "BLOCK").count()
    escalated_count = db.query(Execution).filter(Execution.org_id == org_id, Execution.decision == "ESCALATE").count()

    pending_approvals = db.query(Approval).filter(Approval.org_id == org_id, Approval.status == "PENDING").count()
    verification_failures = db.query(VerificationRecord).filter(VerificationRecord.org_id == org_id, VerificationRecord.status != "VERIFIED").count()
    security_events_count = db.query(SecurityEvent).filter(SecurityEvent.org_id == org_id).count()

    avg_risk = db.query(func.avg(Execution.risk_score)).filter(Execution.org_id == org_id).scalar() or 0.0

    return DashboardStats(
        total_agents=total_agents,
        total_tools=total_tools,
        total_executions=total_executions,
        allowed_count=allowed_count,
        blocked_count=blocked_count,
        escalated_count=escalated_count,
        pending_approvals=pending_approvals,
        verification_failures=verification_failures,
        average_risk_score=round(float(avg_risk), 1),
        security_events_count=security_events_count
    )

@router.get("/recent-executions")
def get_recent_executions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    execs = db.query(Execution).filter(
        Execution.org_id == current_user.org_id
    ).order_by(Execution.created_at.desc()).limit(20).all()

    results = []
    for ex in execs:
        agent = db.query(Agent).filter(Agent.id == ex.agent_id).first()
        results.append({
            "id": ex.id,
            "agent_key": agent.agent_key if agent else "unknown",
            "agent_name": agent.name if agent else "Unknown Agent",
            "tool_name": ex.tool_name,
            "tool_input": ex.tool_input,
            "decision": ex.decision,
            "risk_score": ex.risk_score,
            "risk_factors": ex.risk_factors,
            "status": ex.execution_status,
            "execution_time_ms": ex.execution_time_ms,
            "created_at": ex.created_at
        })

    return results
