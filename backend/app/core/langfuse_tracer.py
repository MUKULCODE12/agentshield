import time
from typing import Dict, Any

class LangfuseTracer:
    """
    Open-source LLM Observability & Tracing logger (Langfuse instrumentation).
    Traces every agent execution step, verification result, and risk score.
    """
    def __init__(self, public_key: str = "lf_pk_demo", secret_key: str = "lf_sk_demo", host: str = "https://cloud.langfuse.com"):
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self.traces = []

    def trace_agent_step(
        self,
        trace_id: str,
        agent_id: str,
        tool_name: str,
        input_payload: Dict[str, Any],
        decision: str,
        risk_score: float,
        verification_status: str
    ) -> Dict[str, Any]:
        trace_event = {
            "trace_id": trace_id,
            "timestamp": time.time(),
            "agent_id": agent_id,
            "name": f"AgentToolCall:{tool_name}",
            "input": input_payload,
            "metadata": {
                "decision": decision,
                "risk_score": risk_score,
                "verification": verification_status
            },
            "status": "SUCCESS" if decision == "ALLOW" else "FLAGGED"
        }
        self.traces.append(trace_event)
        print(f"[Langfuse Observability] Logged trace '{trace_id}' for Agent '{agent_id}' ({decision}).")
        return trace_event

langfuse_tracer = LangfuseTracer()
