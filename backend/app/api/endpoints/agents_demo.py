from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.agents.customer_support import CustomerSupportAgent
from app.api.endpoints.gateway import execute_tool_gateway
from app.schemas.schemas import ToolExecuteRequest

router = APIRouter()

class AgentSimulateRequest(BaseModel):
    user_query: str
    agent_key: str = "agent_support_001"

@router.post("/simulate")
def simulate_agent_run(req: AgentSimulateRequest, db: Session = Depends(get_db)):
    """
    Simulates a Real Customer Support AI Agent receiving a prompt from a customer
    and attempting to call tools through AgentShield Security Gateway.
    """
    query = req.user_query.lower()

    if "refund" in query:
        tool_name = "refund_customer"
        amount = 75000.0 if ("75000" in req.user_query or "75,000" in req.user_query or "75" in req.user_query or "high" in query) else 2500.0
        payload = {"customer_id": "CUST_9921", "amount": amount, "reason": req.user_query}
    elif "email" in query or "notify" in query:
        tool_name = "send_email"
        payload = {"to": "john@acme.com", "subject": "Support Ticket Notice", "body": req.user_query}
    elif "drop" in query or "sql" in query or "delete" in query:
        tool_name = "execute_raw_sql"
        payload = {"query": req.user_query}
    else:
        tool_name = "search_customer"
        payload = {"query": req.user_query}

    # Execute directly via gateway logic internally
    gate_req = ToolExecuteRequest(
        agent_key=req.agent_key,
        tool=tool_name,
        input=payload
    )

    resp = execute_tool_gateway(request=gate_req, x_agent_api_key=None, db=db)

    return {
        "agent_key": req.agent_key,
        "user_query": req.user_query,
        "attempted_tool": tool_name,
        "gateway_response": resp
    }
