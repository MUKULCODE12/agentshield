from sqlalchemy.orm import Session
from app.db.models import Agent, Tool, AgentPermission

class PermissionCheckResult:
    def __init__(self, is_allowed: bool, reason: str = "", max_limit: float = None):
        self.is_allowed = is_allowed
        self.reason = reason
        self.max_limit = max_limit

def check_agent_tool_permission(db: Session, agent: Agent, tool_name: str, payload: dict) -> PermissionCheckResult:
    """
    Checks if the agent has permission to execute the specified tool.
    Also checks financial/volume limits (e.g. refund amount).
    """
    # 1. Find tool in registry
    tool = db.query(Tool).filter(Tool.org_id == agent.org_id, Tool.name == tool_name).first()
    if not tool:
        return PermissionCheckResult(
            is_allowed=False,
            reason=f"Tool '{tool_name}' is not registered in Organization Tool Registry."
        )

    # 2. Find permission record
    perm = db.query(AgentPermission).filter(
        AgentPermission.agent_id == agent.id,
        AgentPermission.tool_id == tool.id
    ).first()

    if not perm or not perm.is_allowed:
        return PermissionCheckResult(
            is_allowed=False,
            reason=f"Agent '{agent.name}' (ID: {agent.agent_key}) does NOT have permission to invoke tool '{tool_name}'."
        )

    # 3. Check write permission requirement if payload implies write/delete
    if tool.is_sensitive and not perm.can_write:
        return PermissionCheckResult(
            is_allowed=False,
            reason=f"Tool '{tool_name}' requires WRITE privileges, but Agent '{agent.name}' only has READ access."
        )

    # 4. Check maximum monetary / batch limits if applicable
    if perm.max_amount_limit is not None and "amount" in payload:
        try:
            requested_amount = float(payload["amount"])
            if requested_amount > perm.max_amount_limit:
                return PermissionCheckResult(
                    is_allowed=False,
                    reason=f"Requested amount ₹{requested_amount:,.2f} exceeds agent's maximum tool limit of ₹{perm.max_amount_limit:,.2f}.",
                    max_limit=perm.max_amount_limit
                )
        except (ValueError, TypeError):
            pass

    return PermissionCheckResult(is_allowed=True, reason="Permission granted.", max_limit=perm.max_amount_limit)
