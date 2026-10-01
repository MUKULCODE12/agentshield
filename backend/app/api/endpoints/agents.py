from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Agent, User, AuditLog, Tool, AgentPermission
from app.schemas.schemas import AgentCreate, AgentOut, AgentWithKeyOut
from app.core.security import generate_agent_api_key
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[AgentOut])
def list_agents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Agent).filter(Agent.org_id == current_user.org_id).all()

@router.post("", response_model=AgentWithKeyOut)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Agent).filter(Agent.agent_key == agent_in.agent_key).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Agent ID '{agent_in.agent_key}' is already registered.")

    raw_api_key, key_hash = generate_agent_api_key(prefix=f"sk_{agent_in.agent_key[:8]}_")

    agent = Agent(
        org_id=current_user.org_id,
        agent_key=agent_in.agent_key,
        name=agent_in.name,
        description=agent_in.description,
        owner=agent_in.owner,
        environment=agent_in.environment,
        status="Active",
        api_key_hash=key_hash
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # Auto-assign permissions to existing org tools
    tools = db.query(Tool).filter(Tool.org_id == current_user.org_id).all()
    for tool in tools:
        is_sensitive = tool.is_sensitive
        perm = AgentPermission(
            agent_id=agent.id,
            tool_id=tool.id,
            is_allowed=not is_sensitive,
            can_read=True,
            can_write=not is_sensitive,
            max_amount_limit=50000.0 if "refund" in tool.name else None
        )
        db.add(perm)
    db.commit()

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="REGISTER_AGENT",
        resource_type="Agent",
        resource_id=agent.agent_key,
        details={"name": agent.name, "owner": agent.owner}
    )
    db.add(audit)
    db.commit()

    return AgentWithKeyOut(
        id=agent.id,
        org_id=agent.org_id,
        agent_key=agent.agent_key,
        name=agent.name,
        description=agent.description,
        owner=agent.owner,
        environment=agent.environment,
        status=agent.status,
        created_at=agent.created_at,
        api_key=raw_api_key
    )

@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.org_id == current_user.org_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}/status")
def toggle_agent_status(agent_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.org_id == current_user.org_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = status
    db.commit()

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="CHANGE_AGENT_STATUS",
        resource_type="Agent",
        resource_id=agent.agent_key,
        details={"new_status": status}
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "agent_key": agent.agent_key, "new_status": status}

@router.post("/{agent_id}/rotate-key")
def rotate_agent_key(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.org_id == current_user.org_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    raw_api_key, key_hash = generate_agent_api_key(prefix=f"sk_{agent.agent_key[:8]}_")
    agent.api_key_hash = key_hash
    db.commit()

    return {"status": "success", "agent_key": agent.agent_key, "new_api_key": raw_api_key}
