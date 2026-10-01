import csv
import io
import json
from typing import List
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import AuditLog, User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("")
def list_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(
        AuditLog.org_id == current_user.org_id
    ).order_by(AuditLog.created_at.desc()).limit(200).all()
    
    return [
        {
            "id": l.id,
            "actor": l.actor,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "created_at": l.created_at
        }
        for l in logs
    ]

@router.get("/export/csv")
def export_audit_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.org_id == current_user.org_id).order_by(AuditLog.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "Actor", "Action", "Resource Type", "Resource ID", "IP Address", "Details"])

    for l in logs:
        writer.writerow([l.id, l.created_at, l.actor, l.action, l.resource_type, l.resource_id, l.ip_address, json.dumps(l.details)])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=agentshield_audit_logs.csv"}
    )
