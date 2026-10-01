from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Approval, Execution
from app.engine.executor import execute_tool
from app.engine.verification import verify_tool_execution
from app.db.models import VerificationRecord, AuditLog

def create_pending_approval(
    db: Session,
    org_id: int,
    execution_id: str,
    agent_id: int,
    tool_name: str,
    tool_input: dict,
    risk_score: float
) -> Approval:
    approval = Approval(
        org_id=org_id,
        execution_id=execution_id,
        agent_id=agent_id,
        tool_name=tool_name,
        tool_input=tool_input,
        risk_score=risk_score,
        status="PENDING",
        requested_at=datetime.utcnow()
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval

def process_approval_decision(
    db: Session,
    approval_id: int,
    action: str, # APPROVE or REJECT
    user_email: str,
    reason: str = None
) -> dict:
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise ValueError("Approval record not found.")

    if approval.status != "PENDING":
        raise ValueError(f"Approval request has already been processed with status '{approval.status}'.")

    execution = db.query(Execution).filter(Execution.id == approval.execution_id).first()
    if not execution:
        raise ValueError("Associated execution record not found.")

    approval.responded_at = datetime.utcnow()
    approval.approved_by = user_email
    approval.rejection_reason = reason

    if action.upper() == "APPROVE":
        approval.status = "APPROVED"
        execution.execution_status = "COMPLETED"
        
        # Execute deferred tool call
        result = execute_tool(approval.tool_name, approval.tool_input or {})
        execution.output_data = result

        # Perform Verification after execution
        claim_text, exp_state, act_state, conf, v_status = verify_tool_execution(
            approval.tool_name, approval.tool_input or {}, result
        )
        ver_rec = VerificationRecord(
            org_id=approval.org_id,
            execution_id=execution.id,
            claim_text=claim_text,
            expected_state=exp_state,
            actual_state=act_state,
            confidence_score=conf,
            status=v_status
        )
        db.add(ver_rec)

        audit = AuditLog(
            org_id=approval.org_id,
            actor=user_email,
            action="APPROVE_ESCALATION",
            resource_type="Approval",
            resource_id=str(approval_id),
            details={"execution_id": execution.id, "tool": approval.tool_name}
        )
        db.add(audit)
        db.commit()
        return {"status": "APPROVED", "result": result, "execution_id": execution.id}

    else:
        approval.status = "REJECTED"
        execution.execution_status = "REJECTED"
        execution.output_data = {"error": "Execution rejected by security administrator", "reason": reason}

        audit = AuditLog(
            org_id=approval.org_id,
            actor=user_email,
            action="REJECT_ESCALATION",
            resource_type="Approval",
            resource_id=str(approval_id),
            details={"execution_id": execution.id, "reason": reason}
        )
        db.add(audit)
        db.commit()
        return {"status": "REJECTED", "execution_id": execution.id}
