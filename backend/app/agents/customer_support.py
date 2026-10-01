import requests
import json
from typing import Dict, Any, List

class CustomerSupportAgent:
    """
    Real AI Agent (Customer Support Agent)
    Connects to AgentShield Gateway for Tool Execution, Permission Validation, Risk Scoring, & Verification.
    """
    def __init__(self, agent_key: str = "agent_support_001", gateway_url: str = "http://localhost:8000/api/v1/gateway/execute"):
        self.agent_key = agent_key
        self.gateway_url = gateway_url
        self.conversation_memory: List[Dict[str, str]] = []

    def execute_tool_via_gateway(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends tool execution request through AgentShield Security Gateway.
        """
        gateway_payload = {
            "agent_key": self.agent_key,
            "tool": tool_name,
            "input": payload,
            "context": {"memory_length": len(self.conversation_memory)}
        }
        
        # Log to local memory
        self.conversation_memory.append({"role": "tool_call", "content": f"Invoking {tool_name} with {json.dumps(payload)}"})

        # In production this makes an HTTP call to the Gateway endpoint
        try:
            res = requests.post(self.gateway_url, json=gateway_payload, timeout=5)
            return res.json()
        except Exception as e:
            return {
                "execution_id": "exec_local_sim",
                "decision": "ERROR",
                "risk_score": 0,
                "risk_factors": [str(e)],
                "status": "FAILED",
                "message": f"Gateway connection error: {str(e)}"
            }

    def process_customer_query(self, user_message: str) -> str:
        """
        Simulates AI agent reasoning and tool invocation based on user query.
        """
        self.conversation_memory.append({"role": "user", "content": user_message})

        msg_lower = user_message.lower()

        if "refund" in msg_lower:
            # Agent decides to call refund_customer tool
            amount = 75000 if "75000" in user_message or "75,000" in user_message or "high" in msg_lower else 2500
            res = self.execute_tool_via_gateway("refund_customer", {
                "customer_id": "CUST_9921",
                "amount": amount,
                "reason": f"Customer request: {user_message}"
            })
            if res.get("decision") == "ALLOW":
                return f"I have processed your refund of ₹{amount:,.2f}. Transaction ID: {res['result'].get('transaction_id')}."
            elif res.get("decision") == "ESCALATE":
                return f"Your refund request of ₹{amount:,.2f} exceeds automatic limits and has been escalated to Security Ops for approval. Approval ID reference: {res.get('execution_id')}."
            else:
                return f"I could not process your refund. Security Gateway Decision: BLOCKED. Reason: {', '.join(res.get('risk_factors', []))}."

        elif "email" in msg_lower or "send" in msg_lower:
            res = self.execute_tool_via_gateway("send_email", {
                "to": "john@acme.com",
                "subject": "Account Status Update",
                "body": "Your support ticket #8891 has been resolved."
            })
            return f"Notification sent to customer. Status: {res.get('decision')}."

        else:
            # Default search customer
            res = self.execute_tool_via_gateway("search_customer", {"query": user_message})
            if res.get("decision") == "ALLOW":
                cust = res.get("result", {}).get("customer", {})
                return f"Found customer details: {cust.get('name')} ({cust.get('email')}), Tier: {cust.get('account_tier')}."
            else:
                return f"Unable to lookup customer due to security block: {res.get('message')}"
