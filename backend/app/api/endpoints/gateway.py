import uuid
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import ToolExecuteRequest, ToolExecuteResponse
from app.engine.identity import authenticate_agent
from app.engine.permission import check_agent_tool_permission
from app.engine.policy import evaluate_organization_policies
from app.engine.risk import analyze_risk
from app.engine.executor import execute_tool
from app.engine.verification import verify_tool_execution
from app.engine.approval import create_pending_approval
from app.db.models import Execution, VerificationRecord, SecurityEvent, AuditLog

router = APIRouter()

@router.post("/execute", response_model=ToolExecuteResponse)
@router.post("/tool/execute", response_model=ToolExecuteResponse)
def execute_tool_gateway(
    request: ToolExecuteRequest,
    x_agent_api_key: Optional[str] = Header(None, alias="X-Agent-API-Key"),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    execution_id = f"exec_{uuid.uuid4().hex[:8]}"

    # Step 1: Agent Authentication & Identity
    agent = authenticate_agent(db, api_key=x_agent_api_key, agent_key=request.agent_key)

    # Step 2: Tool Permission Check
    perm_result = check_agent_tool_permission(db, agent, request.tool, request.input)
    perm_denied_reason = perm_result.reason if not perm_result.is_allowed else None

    # Step 3: Policy Engine Check
    policy_eval = evaluate_organization_policies(db, agent.org_id, request.tool, request.input)

    # Step 4: Advanced AI Risk Assessment & Threat Detection
    risk_assessment = analyze_risk(
        tool_name=request.tool,
        payload=request.input,
        policy_risk=policy_eval.added_risk,
        policy_action=policy_eval.action,
        permission_denied_reason=perm_denied_reason
    )

    decision = risk_assessment.decision
    risk_score = risk_assessment.risk_score
    risk_factors = risk_assessment.risk_factors

    if policy_eval.triggered_policies:
        risk_factors.extend(policy_eval.triggered_policies)

    # Record Security Events if detected
    for sec_ev in risk_assessment.security_events:
        event = SecurityEvent(
            org_id=agent.org_id,
            agent_id=agent.id,
            event_type=sec_ev["type"],
            severity=sec_ev["severity"],
            details=sec_ev["details"],
            blocked=(decision == "BLOCK")
        )
        db.add(event)

    result_data = None
    verification_data = None
    execution_status = "COMPLETED"
    message = ""

    # Step 5: Decision Engine Routing
    if decision == "BLOCK":
        execution_status = "BLOCKED"
        message = f"Execution BLOCKED by AgentShield Security Gateway. Risk Score: {risk_score}/100."
    elif decision == "ESCALATE":
        execution_status = "PENDING_APPROVAL"
        message = f"Execution ESCALATED for Human Approval due to high risk ({risk_score}/100). ID: {execution_id}."
        
        # Create Human Approval queue entry
        create_pending_approval(
            db=db,
            org_id=agent.org_id,
            execution_id=execution_id,
            agent_id=agent.id,
            tool_name=request.tool,
            tool_input=request.input,
            risk_score=risk_score
        )
    else: # ALLOW
        # Step 6: Tool Execution
        result_data = execute_tool(request.tool, request.input)
        
        # Step 7: Independent Verification Engine
        claim_text, exp_state, act_state, confidence, v_status = verify_tool_execution(
            request.tool, request.input, result_data
        )
        ver_rec = VerificationRecord(
            org_id=agent.org_id,
            execution_id=execution_id,
            claim_text=claim_text,
            expected_state=exp_state,
            actual_state=act_state,
            confidence_score=confidence,
            status=v_status
        )
        db.add(ver_rec)
        
        verification_data = {
            "claim": claim_text,
            "confidence": confidence,
            "status": v_status
        }
        message = f"Tool '{request.tool}' executed and independently verified successfully."

    exec_time_ms = round((time.time() - start_time) * 1000, 2)

    # Save Execution Record to DB
    execution = Execution(
        id=execution_id,
        org_id=agent.org_id,
        agent_id=agent.id,
        tool_name=request.tool,
        tool_input=request.input,
        decision=decision,
        risk_score=risk_score,
        risk_factors=risk_factors,
        execution_status=execution_status,
        output_data=result_data,
        execution_time_ms=exec_time_ms
    )
    db.add(execution)

    # Save Audit Trail
    audit = AuditLog(
        org_id=agent.org_id,
        actor=f"Agent:{agent.agent_key}",
        action=f"GATEWAY_{decision}",
        resource_type="Tool",
        resource_id=request.tool,
        details={
            "execution_id": execution_id,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }
    )
    db.add(audit)
    db.commit()

    return ToolExecuteResponse(
        execution_id=execution_id,
        decision=decision,
        risk_score=risk_score,
        risk_factors=risk_factors,
        status=execution_status,
        result=result_data,
        verification=verification_data,
        message=message
    )
