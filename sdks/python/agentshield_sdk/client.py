import requests
from typing import Dict, Any, Optional

class AgentShieldError(Exception):
    pass

class AgentShieldClient:
    """
    Official AgentShield Python SDK (Phase 9)
    Allows AI agents to execute tools securely through the AgentShield Security Gateway.
    
    Usage:
        shield = AgentShieldClient(api_key="sk_agent_support_001_xxxx", endpoint="http://localhost:8000")
        res = shield.execute(tool="send_email", input={"to": "john@acme.com", "subject": "Hello"})
    """
    def __init__(self, api_key: str, endpoint: str = "http://localhost:8000", agent_key: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.agent_key = agent_key

    def execute(self, tool: str, input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.endpoint}/v1/tool/execute"
        headers = {
            "Content-Type": "application/json",
            "X-Agent-API-Key": self.api_key
        }
        payload = {
            "tool": tool,
            "input": input,
            "context": context
        }
        if self.agent_key:
            payload["agent_key"] = self.agent_key

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 401:
                raise AgentShieldError("Authentication failed: Invalid Agent API Key")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise AgentShieldError(f"AgentShield Gateway request failed: {str(e)}")
