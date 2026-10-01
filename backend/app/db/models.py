from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    plan = Column(String(50), default="Enterprise") # Free, Pro, Enterprise
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    tools = relationship("Tool", back_populates="organization")
    policies = relationship("Policy", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Security Admin") # Admin, Security Admin, Viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    agent_key = Column(String(50), unique=True, index=True, nullable=False) # e.g. agent_support_001
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=False)
    environment = Column(String(50), default="Production") # Staging, Production
    status = Column(String(50), default="Active") # Active, Suspended, Inactive
    api_key_hash = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="agents")
    permissions = relationship("AgentPermission", back_populates="agent", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="agent")

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), index=True, nullable=False) # e.g. search_customer
    display_name = Column(String(100), nullable=False)
    category = Column(String(50), default="General") # Customer, Finance, Database, Communication
    description = Column(Text, nullable=True)
    schema_json = Column(JSON, nullable=True)
    is_sensitive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="tools")
    permissions = relationship("AgentPermission", back_populates="tool", cascade="all, delete-orphan")

class AgentPermission(Base):
    __tablename__ = "agent_permissions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)
    is_allowed = Column(Boolean, default=True)
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    max_amount_limit = Column(Float, nullable=True) # e.g. 50000.0 for refund
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="permissions")
    tool = relationship("Tool", back_populates="permissions")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), default="Security") # Compliance, Financial, Data Leakage, Behavioral
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), default="KEYWORDS") # KEYWORDS, THRESHOLD, REGEX, PROMPT_INJECTION
    content = Column(Text, nullable=False) # JSON rules or text patterns
    action_on_trigger = Column(String(20), default="BLOCK") # BLOCK, ESCALATE, ALERT
    risk_score_weight = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="policies")

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(50), primary_key=True, index=True) # e.g. exec_89dfa123
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSON, nullable=True)
    decision = Column(String(20), nullable=False) # ALLOW, BLOCK, ESCALATE
    risk_score = Column(Float, default=0.0) # 0 to 100
    risk_factors = Column(JSON, nullable=True) # list of reason strings
    execution_status = Column(String(50), default="COMPLETED") # COMPLETED, BLOCKED, PENDING_APPROVAL, REJECTED, FAILED
    output_data = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="executions")
    approval = relationship("Approval", back_populates="execution", uselist=False)
    verification = relationship("VerificationRecord", back_populates="execution", uselist=False)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    execution_id = Column(String(50), ForeignKey("executions.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSON, nullable=True)
    risk_score = Column(Float, default=0.0)
    status = Column(String(20), default="PENDING") # PENDING, APPROVED, REJECTED, TIMEOUT
    requested_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    execution = relationship("Execution", back_populates="approval")

class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    execution_id = Column(String(50), ForeignKey("executions.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    expected_state = Column(JSON, nullable=True)
    actual_state = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=1.0) # 0.0 to 1.0
    status = Column(String(20), default="VERIFIED") # VERIFIED, MISMATCH, FAILED
    verified_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("Execution", back_populates="verification")

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    event_type = Column(String(50), nullable=False) # PROMPT_INJECTION, DATA_EXFILTRATION, UNAUTHORIZED_TOOL, HIGH_RISK_ANOMALY
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    details = Column(JSON, nullable=True)
    blocked = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    created_at = Column(DateTime, default=datetime.utcnow)
