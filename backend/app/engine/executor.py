import time
from typing import Dict, Any

def execute_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the requested tool action safely and returns structured output.
    Supports real business tools (Customer DB, Communications, Financials, Dev Tools).
    """
    start_time = time.time()

    if tool_name == "search_customer":
        query = payload.get("query") or payload.get("customer_id") or payload.get("email", "john@acme.com")
        result = {
            "status": "success",
            "customer": {
                "customer_id": "CUST_9921",
                "name": "John Doe",
                "email": "john@acme.com",
                "account_tier": "VIP Gold",
                "total_orders": 14,
                "status": "Active",
                "matched_query": str(query)
            }
        }
    elif tool_name == "update_customer":
        customer_id = payload.get("customer_id", "CUST_9921")
        field = payload.get("field", "status")
        value = payload.get("value", "VIP_Verified")
        result = {
            "status": "success",
            "customer_id": customer_id,
            "updated_field": field,
            "new_value": value,
            "message": f"Successfully updated customer {customer_id} field '{field}' to '{value}'."
        }
    elif tool_name == "send_email":
        to_email = payload.get("to") or payload.get("email", "customer@example.com")
        subject = payload.get("subject", "Support Notification")
        body = payload.get("body", "Thank you for contacting customer support.")
        result = {
            "status": "delivered",
            "message_id": f"msg_mail_{int(time.time())}",
            "recipient": to_email,
            "subject": subject,
            "body_snippet": body[:80] + "..." if len(body) > 80 else body
        }
    elif tool_name == "refund_customer":
        customer_id = payload.get("customer_id", "CUST_9921")
        amount = payload.get("amount", 0.0)
        reason = payload.get("reason", "Customer satisfaction request")
        result = {
            "status": "processed",
            "transaction_id": f"tx_ref_{int(time.time())}",
            "customer_id": customer_id,
            "refund_amount": float(amount),
            "currency": "INR",
            "reason": reason,
            "message": f"Refund of ₹{float(amount):,.2f} successfully credited to customer {customer_id}."
        }
    elif tool_name == "send_slack_alert":
        channel = payload.get("channel", "#security-alerts")
        message = payload.get("message", "Agent alert triggered")
        result = {
            "status": "sent",
            "channel": channel,
            "timestamp": time.time(),
            "preview": message
        }
    elif tool_name == "github_create_issue":
        repo = payload.get("repo", "acme/agentshield")
        title = payload.get("title", "Automated Security Finding")
        result = {
            "status": "created",
            "issue_number": 42,
            "issue_url": f"https://github.com/{repo}/issues/42",
            "title": title
        }
    elif tool_name == "execute_raw_sql":
        query = payload.get("query", "SELECT 1")
        result = {
            "status": "executed",
            "rows_affected": 0,
            "data": [],
            "query": query
        }
    else:
        result = {
            "status": "executed",
            "tool": tool_name,
            "payload_received": payload,
            "message": f"Tool '{tool_name}' executed successfully."
        }

    return result
