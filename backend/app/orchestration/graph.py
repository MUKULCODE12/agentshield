import time
import json
from typing import Dict, Any, List, TypedDict
from app.engine.executor import execute_tool
from app.engine.verification import verify_tool_execution
from app.engine.policy import evaluate_organization_policies
from app.engine.risk import analyze_risk

# LangGraph State Schema
class AgentState(TypedDict):
    agent_id: str
    tool_name: str
    claimed_input: Dict[str, Any]
    claimed_action: str
    actual_state: Dict[str, Any]
    verification_status: str
    verification_confidence: float
    rag_policy_matches: List[str]
    policy_violation: bool
    risk_score: float
    trust_score: float
    report_summary: str

# 1. Subject Agent Node
def subject_agent_node(state: AgentState) -> AgentState:
    """Executes tool action and claims success."""
    tool = state["tool_name"]
    inp = state["claimed_input"]
    result = execute_tool(tool, inp)
    state["claimed_action"] = f"Claimed execution of '{tool}' with payload {json.dumps(inp)}"
    return state

# 2. Monitor Agent Node
def monitor_agent_node(state: AgentState) -> AgentState:
    """Watches agent action stream in real-time."""
    print(f"[Monitor Agent] Captured claimed action from agent '{state['agent_id']}': {state['claimed_action']}")
    return state

# 3. Verifier Agent Node
def verifier_agent_node(state: AgentState) -> AgentState:
    """Independently checks actual system state (DB query, mail log)."""
    tool = state["tool_name"]
    inp = state["claimed_input"]
    result = execute_tool(tool, inp)
    
    claim, exp, act, conf, status = verify_tool_execution(tool, inp, result)
    state["actual_state"] = act
    state["verification_confidence"] = conf
    state["verification_status"] = status
    return state

# 4. RAG Policy-Match Agent Node
def rag_policy_match_node(state: AgentState) -> AgentState:
    """Retrieves policy docs from RAG vector store and judges compliance vs violation."""
    inp = state["claimed_input"]
    tool = state["tool_name"]
    
    # Check policies
    eval_res = evaluate_organization_policies(db=None, org_id=1, tool_name=tool, payload=inp)
    state["rag_policy_matches"] = eval_res.triggered_policies
    state["policy_violation"] = (eval_res.action == "BLOCK")
    return state

# 5. Risk Classifier Node (LoRA / Rule engine)
def risk_classifier_node(state: AgentState) -> AgentState:
    """Scores action pattern risk (Low / Medium / High)."""
    risk_res = analyze_risk(
        tool_name=state["tool_name"],
        payload=state["claimed_input"],
        policy_risk=50.0 if state["policy_violation"] else 0.0,
        policy_action="BLOCK" if state["policy_violation"] else "ALLOW"
    )
    state["risk_score"] = risk_res.risk_score
    return state

# 6. Trust-Scoring Node
def trust_scoring_node(state: AgentState) -> AgentState:
    """Aggregates verification, policy match, and risk into a Trust Score (0 - 100)."""
    base_trust = 100.0
    if state["verification_status"] != "VERIFIED":
        base_trust -= 50.0
    if state["policy_violation"]:
        base_trust -= 40.0
    base_trust -= (state["risk_score"] * 0.3)
    
    state["trust_score"] = max(0.0, round(base_trust, 1))
    return state

# 7. Reporter Agent Node
def reporter_agent_node(state: AgentState) -> AgentState:
    """Generates audit-ready compliance report."""
    trust = state["trust_score"]
    status = "TRUSTED" if trust >= 70 else "WARNING" if trust >= 40 else "UNTRUSTED"
    state["report_summary"] = (
        f"Sentinel Compliance Audit: Agent '{state['agent_id']}' score {trust}/100 ({status}). "
        f"Verified State: {state['verification_status']}. Policy Violations: {len(state['rag_policy_matches'])}."
    )
    return state

class SentinelLangGraphPipeline:
    """
    Executes the full 7-step Sentinel LangGraph state machine.
    """
    def run_pipeline(self, agent_id: str, tool_name: str, tool_input: Dict[str, Any]) -> AgentState:
        state: AgentState = {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "claimed_input": tool_input,
            "claimed_action": "",
            "actual_state": {},
            "verification_status": "PENDING",
            "verification_confidence": 0.0,
            "rag_policy_matches": [],
            "policy_violation": False,
            "risk_score": 0.0,
            "trust_score": 100.0,
            "report_summary": ""
        }

        state = subject_agent_node(state)
        state = monitor_agent_node(state)
        state = verifier_agent_node(state)
        state = rag_policy_match_node(state)
        state = risk_classifier_node(state)
        state = trust_scoring_node(state)
        state = reporter_agent_node(state)

        return state

sentinel_graph = SentinelLangGraphPipeline()
