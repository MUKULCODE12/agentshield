from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Tool, User, Agent, AgentPermission, AuditLog
from app.schemas.schemas import ToolCreate, ToolOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[ToolOut])
def list_tools(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tools = db.query(Tool).filter(Tool.org_id == current_user.org_id).all()
    results = []
    for t in tools:
        results.append(ToolOut(
            id=t.id,
            org_id=t.org_id,
            name=t.name,
            display_name=t.display_name,
            category=t.category,
            description=t.description,
            tool_schema=t.schema_json,
            is_sensitive=t.is_sensitive,
            created_at=t.created_at
        ))
    return results

@router.post("", response_model=ToolOut)
def register_tool(tool_in: ToolCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Tool).filter(Tool.org_id == current_user.org_id, Tool.name == tool_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tool '{tool_in.name}' is already registered.")

    tool = Tool(
        org_id=current_user.org_id,
        name=tool_in.name,
        display_name=tool_in.display_name,
        category=tool_in.category,
        description=tool_in.description,
        schema_json=tool_in.tool_schema,
        is_sensitive=tool_in.is_sensitive
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)

    # Auto create permission matrix records for existing agents
    agents = db.query(Agent).filter(Agent.org_id == current_user.org_id).all()
    for ag in agents:
        perm = AgentPermission(
            agent_id=ag.id,
            tool_id=tool.id,
            is_allowed=not tool.is_sensitive,
            can_read=True,
            can_write=not tool.is_sensitive
        )
        db.add(perm)
    db.commit()

    audit = AuditLog(
        org_id=current_user.org_id,
        actor=current_user.email,
        action="REGISTER_TOOL",
        resource_type="Tool",
        resource_id=tool.name,
        details={"category": tool.category, "is_sensitive": tool.is_sensitive}
    )
    db.add(audit)
    db.commit()

    return ToolOut(
        id=tool.id,
        org_id=tool.org_id,
        name=tool.name,
        display_name=tool.display_name,
        category=tool.category,
        description=tool.description,
        tool_schema=tool.schema_json,
        is_sensitive=tool.is_sensitive,
        created_at=tool.created_at
    )
