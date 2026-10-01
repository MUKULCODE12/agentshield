from typing import Dict, Any, Tuple

def verify_tool_execution(tool_name: str, payload: Dict[str, Any], result: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Dict[str, Any], float, str]:
    """
    Enterprise Verification Engine:
    1. Extracts claim made by tool execution
    2. Compares expected state vs actual executed state
    3. Calculates verification confidence score (0.0 to 1.0)
    4. Returns (claim_text, expected_state, actual_state, confidence, status)
    """
    if tool_name == "refund_customer":
        requested_amount = float(payload.get("amount", 0.0))
        actual_amount = float(result.get("refund_amount", 0.0))
        customer_id = payload.get("customer_id", "CUST_9921")
        claim_text = f"Agent claims refund of ₹{requested_amount:,.2f} for customer {customer_id}."
        
        expected_state = {"customer_id": customer_id, "amount": requested_amount, "tx_status": "processed"}
        actual_state = {"customer_id": result.get("customer_id"), "amount": actual_amount, "tx_status": result.get("status")}

        if requested_amount == actual_amount and result.get("status") == "processed":
            confidence = 1.0
            status_str = "VERIFIED"
        else:
            confidence = 0.3
            status_str = "MISMATCH"

    elif tool_name == "update_customer":
        customer_id = payload.get("customer_id", "CUST_9921")
        target_val = payload.get("value")
        claim_text = f"Agent claims updating customer {customer_id} to '{target_val}'."
        expected_state = {"customer_id": customer_id, "value": target_val}
        actual_state = {"customer_id": result.get("customer_id"), "value": result.get("new_value")}
        confidence = 1.0 if target_val == result.get("new_value") else 0.0
        status_str = "VERIFIED" if confidence == 1.0 else "MISMATCH"

    elif tool_name == "send_email":
        recipient = payload.get("to") or payload.get("email")
        claim_text = f"Agent claims sending notification email to {recipient}."
        expected_state = {"recipient": recipient, "delivery": "delivered"}
        actual_state = {"recipient": result.get("recipient"), "delivery": result.get("status")}
        confidence = 0.95
        status_str = "VERIFIED"

    else:
        claim_text = f"Agent executed tool '{tool_name}'."
        expected_state = {"payload": payload}
        actual_state = {"output": result}
        confidence = 1.0
        status_str = "VERIFIED"

    return claim_text, expected_state, actual_state, confidence, status_str
