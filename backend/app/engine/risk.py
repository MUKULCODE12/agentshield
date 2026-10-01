import re
import json
from typing import Dict, Any, List, Tuple

class RiskAssessment:
    def __init__(self, risk_score: float, decision: str, risk_factors: List[str], security_events: List[Dict[str, Any]]):
        self.risk_score = min(100.0, max(0.0, risk_score))
        self.decision = decision # ALLOW, BLOCK, ESCALATE
        self.risk_factors = risk_factors
        self.security_events = security_events

# Prompt injection signatures
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"system prompt override",
    r"you are now in developer mode",
    r"jailbreak",
    r"bypass security policies",
    r"do anything now",
    r"dan mode",
    r"admin access granted",
    r"drop table",
    r"exec\s+sp_executesql",
    r"eval\(",
    r"base64_decode"
]

# PII and Credential leakage patterns
PII_PATTERNS = {
    "CREDIT_CARD": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "API_KEY": r"(sk_live_[a-f0-9]{32,64}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36})",
    "PASSWORD": r"(?:password|passwd|secret)\s*[:=]\s*['\"]([^'\"]+)['\"]"
}

def analyze_risk(
    tool_name: str,
    payload: Dict[str, Any],
    policy_risk: float,
    policy_action: str,
    permission_denied_reason: str = None
) -> RiskAssessment:
    """
    Performs comprehensive multi-layer security risk evaluation.
    1. Permission check validation
    2. Prompt Injection Detection
    3. Data Exfiltration & PII Leakage Detection
    4. Tool Abuse & Anomaly Detection
    5. Composite Risk Scoring (0 - 100) & Decision Routing
    """
    risk_score = policy_risk
    risk_factors: List[str] = []
    security_events: List[Dict[str, Any]] = []

    # If permission was denied by permission matrix, immediate block
    if permission_denied_reason:
        risk_score += 80.0
        risk_factors.append(f"UNAUTHORIZED_TOOL: {permission_denied_reason}")
        security_events.append({
            "type": "UNAUTHORIZED_TOOL",
            "severity": "HIGH",
            "details": {"tool": tool_name, "reason": permission_denied_reason}
        })

    payload_str = json.dumps(payload)

    # 1. Prompt Injection Detection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, payload_str, re.IGNORECASE):
            risk_score += 85.0
            risk_factors.append(f"PROMPT_INJECTION_DETECTED: Input matches suspicious pattern '{pattern}'")
            security_events.append({
                "type": "PROMPT_INJECTION",
                "severity": "CRITICAL",
                "details": {"pattern": pattern, "payload_snippet": payload_str[:200]}
            })

    # 2. Data Exfiltration & Credential Protection
    for pii_type, pii_regex in PII_PATTERNS.items():
        if re.search(pii_regex, payload_str):
            risk_score += 65.0
            risk_factors.append(f"DATA_EXFILTRATION_RISK: Payload contains sensitive pattern '{pii_type}'")
            security_events.append({
                "type": "DATA_EXFILTRATION",
                "severity": "HIGH",
                "details": {"pii_type": pii_type}
            })

    # 3. Tool Abuse & High Value Anomaly Detection
    if tool_name in ["refund_customer", "process_payout"]:
        amount = payload.get("amount", 0)
        try:
            val = float(amount)
            if val >= 50000:
                risk_score += 50.0
                risk_factors.append(f"HIGH_VALUE_TRANSACTION: Refund amount ₹{val:,.2f} requires human verification")
            elif val > 10000:
                risk_score += 25.0
                risk_factors.append(f"ELEVATED_TRANSACTION: Refund amount ₹{val:,.2f}")
        except (ValueError, TypeError):
            pass

    if tool_name in ["execute_raw_sql", "admin_database"]:
        risk_score += 90.0
        risk_factors.append("CRITICAL_DATABASE_ACCESS: Direct database mutation tool invoked")
        security_events.append({
            "type": "HIGH_RISK_ANOMALY",
            "severity": "CRITICAL",
            "details": {"tool": tool_name}
        })

    if tool_name == "send_email":
        recipients = payload.get("recipients", [])
        if isinstance(recipients, list) and len(recipients) > 20:
            risk_score += 45.0
            risk_factors.append(f"BULK_ACTION_DETECTED: Batch email sending to {len(recipients)} recipients")

    # Determine Final Decision
    decision = "ALLOW"
    
    if permission_denied_reason or policy_action == "BLOCK" or risk_score >= 75.0:
        decision = "BLOCK"
    elif policy_action == "ESCALATE" or risk_score >= 40.0:
        decision = "ESCALATE"
    else:
        decision = "ALLOW"

    return RiskAssessment(
        risk_score=min(100.0, risk_score),
        decision=decision,
        risk_factors=risk_factors,
        security_events=security_events
    )
