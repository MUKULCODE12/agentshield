import json
import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Policy

class PolicyEvaluationResult:
    def __init__(self, action: str, triggered_policies: List[str], added_risk: float):
        self.action = action # ALLOW, BLOCK, ESCALATE
        self.triggered_policies = triggered_policies
        self.added_risk = added_risk

def evaluate_organization_policies(db: Session = None, org_id: int = 1, tool_name: str = "", payload: dict = {}) -> PolicyEvaluationResult:
    """
    Evaluates active organization policies against the tool execution request.
    Returns composite policy decision (BLOCK/ESCALATE/ALLOW), triggered policies list, and risk score contribution.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        active_policies = db.query(Policy).filter(
            Policy.org_id == org_id,
            Policy.is_active == True
        ).all()

        payload_str = json.dumps(payload).lower()
        triggered = []
        added_risk = 0.0
        highest_action = "ALLOW"

        action_priority = {"ALLOW": 1, "ESCALATE": 2, "BLOCK": 3}

        for policy in active_policies:
            rule = policy.content.lower()
            rule_type = policy.rule_type.upper()
            matched = False

            if rule_type == "KEYWORDS":
                keywords = [k.strip() for k in rule.split(",") if k.strip()]
                for kw in keywords:
                    if kw in payload_str or kw in tool_name.lower():
                        matched = True
                        break
            elif rule_type == "REGEX":
                try:
                    if re.search(rule, payload_str):
                        matched = True
                except re.error:
                    pass
            elif rule_type == "THRESHOLD":
                try:
                    if "amount" in payload:
                        val = float(payload["amount"])
                        limit = float(rule)
                        if val > limit:
                            matched = True
                except ValueError:
                    pass

            if matched:
                triggered.append(f"[{policy.category}] {policy.title}")
                added_risk += policy.risk_score_weight
                if action_priority.get(policy.action_on_trigger, 1) > action_priority.get(highest_action, 1):
                    highest_action = policy.action_on_trigger

        return PolicyEvaluationResult(
            action=highest_action,
            triggered_policies=triggered,
            added_risk=added_risk
        )
    finally:
        if close_session:
            db.close()
