from typing import Dict, Any, List
from fastapi import APIRouter
from app.engine.executor import execute_tool

router = APIRouter()

# MCP Tool Definitions Schema
MCP_REGISTERED_TOOLS = [
    {
        "name": "search_customer",
        "description": "Searches customer database by email or ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Email or Customer ID"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "refund_customer",
        "description": "Issues monetary refund to customer account through AgentShield Gateway.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "amount": {"type": "number"},
                "reason": {"type": "string"}
            },
            "required": ["customer_id", "amount"]
        }
    },
    {
        "name": "send_email",
        "description": "Sends customer email notification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["to", "subject", "body"]
        }
    }
]

@router.post("/jsonrpc")
def mcp_jsonrpc_endpoint(payload: Dict[str, Any]):
    """
    Standardized Model Context Protocol (MCP) JSON-RPC 2.0 endpoint.
    Handles 'tools/list' and 'tools/call'.
    """
    method = payload.get("method")
    req_id = payload.get("id", 1)

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_REGISTERED_TOOLS
            }
        }
    elif method == "tools/call":
        params = payload.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result_data = execute_tool(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(result_data)
                    }
                ],
                "isError": False
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not supported"}
        }
