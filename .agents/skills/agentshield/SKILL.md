---
name: agentshield
description: >-
  Integrate and interact with AgentShield / Sentinel Enterprise AI Security Gateway.
  Use to audit tool execution risks, query policy compliance, register agents, and inspect security events.
---

# AgentShield / Sentinel AI Security Integration Skill

This skill connects Antigravity directly to the **AgentShield AI Security & Compliance Gateway**.

## Features & Capabilities

1. **Tool Execution Proxying**: Route tool calls through AgentShield's zero-trust gateway (`/v1/tool/execute`).
2. **Model Context Protocol (MCP)**: Interact via JSON-RPC endpoint (`/mcp/jsonrpc`).
3. **Fleet Security Auditing**: Query active agent identities, risk scores, and human approval queues.
4. **Policy Compliance Evaluation**: Evaluate natural language tool payloads against HIPAA, SOC 2, and internal corporate security guidelines.

---

## Quick Reference Commands & Endpoints

| Action | API Endpoint | Method |
| :--- | :--- | :--- |
| **Check Gateway Status** | `http://localhost:8000/` | `GET` |
| **Execute Tool via Gateway** | `http://localhost:8000/v1/tool/execute` | `POST` |
| **MCP JSON-RPC Endpoint** | `http://localhost:8000/mcp/jsonrpc` | `POST` |
| **Run 7-Step Simulation** | `http://localhost:8000/api/v1/agents-demo/simulate` | `POST` |
| **Get Overview Analytics** | `http://localhost:8000/api/v1/analytics/overview` | `GET` |

---

## Example Usage: Python SDK Integration

To route any tool call through AgentShield security gateway in Python:

```python
import requests

AGENT_API_KEY = "ag_key_sec_ops_9921"
GATEWAY_URL = "http://localhost:8000/v1/tool/execute" # Or AWS Cloud URL

def execute_secure_tool(tool_name: str, payload: dict):
    headers = {
        "X-Agent-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "tool_name": tool_name,
        "arguments": payload
    }
    
    response = requests.post(GATEWAY_URL, json=body, headers=headers)
    result = response.json()
    
    if result.get("status") == "BLOCKED":
        raise Exception(f"Security Alert: Tool execution blocked by AgentShield. Reason: {result.get('reason')}")
    elif result.get("status") == "ESCALATED":
        return "Tool execution pending Human-in-the-Loop authorization in AgentShield Dashboard."
    
    return result.get("output")
```

---

## MCP Server Integration

Add the following to your Antigravity `mcp_config.json`:

```json
{
  "mcpServers": {
    "agentshield": {
      "url": "http://localhost:8000/mcp/jsonrpc",
      "transport": "http",
      "headers": {
        "X-Agent-API-Key": "ag_key_sec_ops_9921"
      }
    }
  }
}
```
