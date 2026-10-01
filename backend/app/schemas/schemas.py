from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: int
    org_id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

# --- Agent Schemas ---
class AgentCreate(BaseModel):
    agent_key: str = Field(..., example="agent_support_001")
    name: str = Field(..., example="Customer Support Agent")
    description: Optional[str] = None
    owner: str = Field(..., example="Acme Corp Operations")
    environment: str = Field("Production", example="Production")

class AgentOut(BaseModel):
    id: int
    org_id: int
    agent_key: str
    name: str
    description: Optional[str]
    owner: str
    environment: str
    status: str
    created_at: datetime

class AgentWithKeyOut(AgentOut):
    api_key: str # Raw API key shown only upon creation!

# --- Tool Schemas ---
class ToolCreate(BaseModel):
    name: str
    display_name: str
    category: str = "General"
    description: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    is_sensitive: bool = False

class ToolOut(BaseModel):
    id: int
    org_id: int
    name: str
    display_name: str
    category: str
    description: Optional[str]
    tool_schema: Optional[Dict[str, Any]] = None
    is_sensitive: bool
    created_at: datetime

# --- Permission Schemas ---
class PermissionSet(BaseModel):
    agent_id: int
    tool_id: int
    is_allowed: bool
    can_read: bool = True
    can_write: bool = False
    max_amount_limit: Optional[float] = None

class PermissionOut(BaseModel):
    id: int
    agent_id: int
    tool_id: int
    tool_name: str
    is_allowed: bool
    can_read: bool
    can_write: bool
    max_amount_limit: Optional[float]

# --- Gateway Execute Schemas ---
class ToolExecuteRequest(BaseModel):
    agent_key: Optional[str] = None
    tool: str
    input: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None

class ToolExecuteResponse(BaseModel):
    execution_id: str
    decision: str # ALLOW, BLOCK, ESCALATE
    risk_score: float
    risk_factors: List[str]
    status: str
    result: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    message: str

# --- Policy Schemas ---
class PolicyCreate(BaseModel):
    title: str
    category: str = "Security"
    description: Optional[str] = None
    rule_type: str = "KEYWORDS"
    content: str
    action_on_trigger: str = "BLOCK"
    risk_score_weight: int = 30
    is_active: bool = True

class PolicyOut(BaseModel):
    id: int
    org_id: int
    title: str
    category: str
    description: Optional[str]
    rule_type: str
    content: str
    action_on_trigger: str
    risk_score_weight: int
    is_active: bool
    version: int
    created_at: datetime

# --- Approval Schemas ---
class ApprovalOut(BaseModel):
    id: int
    org_id: int
    execution_id: str
    agent_id: int
    agent_name: str
    tool_name: str
    tool_input: Dict[str, Any]
    risk_score: float
    status: str
    requested_at: datetime
    responded_at: Optional[datetime]
    approved_by: Optional[str]
    rejection_reason: Optional[str]

class ApprovalAction(BaseModel):
    action: str # APPROVE or REJECT
    reason: Optional[str] = None

# --- Verification Schemas ---
class VerificationOut(BaseModel):
    id: int
    execution_id: str
    claim_text: str
    expected_state: Optional[Dict[str, Any]]
    actual_state: Optional[Dict[str, Any]]
    confidence_score: float
    status: str
    verified_at: datetime

# --- Security Event Schemas ---
class SecurityEventOut(BaseModel):
    id: int
    event_type: str
    severity: str
    details: Dict[str, Any]
    blocked: bool
    created_at: datetime

# --- Analytics Schemas ---
class DashboardStats(BaseModel):
    total_agents: int
    total_tools: int
    total_executions: int
    allowed_count: int
    blocked_count: int
    escalated_count: int
    pending_approvals: int
    verification_failures: int
    average_risk_score: float
    security_events_count: int
