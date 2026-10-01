from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import AgentPermission, Agent, Tool, User, AuditLog
from app.schemas.schemas import PermissionSet, PermissionOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/matrix")
def get_permission_matrix(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agents = db.query(Agent).filter(Agent.org_id == current_user.org_id).all()
    tools = db.query(Tool).filter(Tool.org_id == current_user.org_id).all()

    matrix = []
    for ag in agents:
        agent_perms = []
        for tl in tools:
            perm = db.query(AgentPermission).filter(
                AgentPermission.agent_id == ag.id,
                AgentPermission.tool_id == tl.id
            ).first()

            if not perm:
                # Default fallback
                perm = AgentPermission(
                    agent_id=ag.id,
                    tool_id=tl.id,
                    is_allowed=False,
                    can_read=True,
                    can_write=False
                )
                db.add(perm)
                db.commit()
                db.refresh(perm)

            agent_perms.append({
                "permission_id": perm.id,
                "tool_id": tl.id,
                "tool_name": tl.name,
                "tool_display": tl.display_name,
                "category": tl.category,
                "is_sensitive": tl.is_sensitive,
                "is_allowed": perm.is_allowed,
                "can_read": perm.can_read,
                "can_write": perm.can_write,
                "max_amount_limit": perm.max_amount_limit
            })

        matrix.append({
            "agent_id": ag.id,
            "agent_key": ag.agent_key,
            "agent_name": ag.name,
            "owner": ag.owner,
            "environment": ag.environment,
            "permissions": agent_perms
        })

    return matrix

@router.post("/update")
def update_permission(perm_in: PermissionSet, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    perm = db.query(AgentPermission).filter(
        AgentPermission.agent_id == perm_in.agent_id,
        AgentPermission.tool_id == perm_in.tool_id
    ).first()

    if not perm:
        perm = AgentPermission(
            agent_id=perm_in.agent_id,
            tool_id=perm_in.tool_id
        )
        db.add(perm)

    perm.is_allowed = perm_in.is_allowed
    perm.can_read = perm_in.can_read
    perm.can_write = perm_in.can_write
    perm.max_amount_limit = perm_in.max_amount_limit
    db.commit()

    agent = db.query(Agent).filter(Agent.id == perm_in.agent_id).first()
    tool = db.query(Tool).filter(Tool.id == perm_in.tool_id).first()

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="UPDATE_PERMISSION",
        resource_type="Permission",
        resource_id=f"agent_{perm_in.agent_id}_tool_{perm_in.tool_id}",
        details={
            "agent": agent.agent_key if agent else perm_in.agent_id,
            "tool": tool.name if tool else perm_in.tool_id,
            "is_allowed": perm_in.is_allowed,
            "max_amount_limit": perm_in.max_amount_limit
        }
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "message": "Permission updated successfully."}
