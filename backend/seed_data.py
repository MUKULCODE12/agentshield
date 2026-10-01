import sys
import os
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.db.models import Organization, User, Agent, Tool, AgentPermission, Policy, Execution, Approval, VerificationRecord, SecurityEvent, AuditLog
from app.core.security import get_password_hash, generate_agent_api_key

def seed_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Organization).first():
            print("Database already contains seeded data.")
            return

        print("Seeding production AgentShield database...")

        # 1. Organization
        org = Organization(name="Acme Corp Enterprise", slug="acme-corp", plan="Enterprise")
        db.add(org)
        db.commit()
        db.refresh(org)

        # 2. Users
        admin_user = User(
            org_id=org.id,
            email="admin@agentshield.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Security Admin",
            role="Admin"
        )
        db.add(admin_user)
        db.commit()

        # 3. Tools
        tools_def = [
            ("search_customer", "Search Customer DB", "Customer", "Look up customer profile and account details", False),
            ("update_customer", "Update Customer Profile", "Customer", "Modify customer attributes or status", True),
            ("send_email", "Send Email Notification", "Communication", "Send outbound email to customer or partner", False),
            ("refund_customer", "Process Customer Refund", "Finance", "Issue monetary credit or refund to customer account", True),
            ("send_slack_alert", "Send Slack Notification", "Communication", "Post notification to Slack channel", False),
            ("github_create_issue", "Create GitHub Issue", "Developer", "Create issue on GitHub repository", False),
            ("execute_raw_sql", "Execute Raw SQL Query", "Database", "Direct SQL execution on production database", True)
        ]

        tool_objects = {}
        for name, dname, cat, desc, sens in tools_def:
            t = Tool(
                org_id=org.id,
                name=name,
                display_name=dname,
                category=cat,
                description=desc,
                schema_json={"type": "object", "properties": {"customer_id": {"type": "string"}}},
                is_sensitive=sens
            )
            db.add(t)
            tool_objects[name] = t
        db.commit()
        for k, v in tool_objects.items():
            db.refresh(v)

        # 4. Agents
        agents_def = [
            ("agent_support_001", "Customer Support AI Agent", "Handles customer support queries and refund requests", "Acme Ops", "Production"),
            ("agent_sales_002", "Sales & Marketing Agent", "Outreach and email follow-ups", "Growth Team", "Production"),
            ("agent_dev_003", "DevOps Assistant Agent", "Automates GitHub issues and infrastructure alerts", "Engineering", "Staging")
        ]

        agent_objects = {}
        for akey, name, desc, owner, env in agents_def:
            raw_key, key_hash = generate_agent_api_key(prefix=f"sk_{akey[:10]}_")
            ag = Agent(
                org_id=org.id,
                agent_key=akey,
                name=name,
                description=desc,
                owner=owner,
                environment=env,
                status="Active",
                api_key_hash=key_hash
            )
            db.add(ag)
            agent_objects[akey] = (ag, raw_key)
        db.commit()

        support_ag = agent_objects["agent_support_001"][0]
        sales_ag = agent_objects["agent_sales_002"][0]
        dev_ag = agent_objects["agent_dev_003"][0]

        # 5. Tool Authorization Matrix (Permissions)
        # Support Agent permissions
        db.add(AgentPermission(agent_id=support_ag.id, tool_id=tool_objects["search_customer"].id, is_allowed=True, can_read=True, can_write=False))
        db.add(AgentPermission(agent_id=support_ag.id, tool_id=tool_objects["update_customer"].id, is_allowed=True, can_read=True, can_write=True))
        db.add(AgentPermission(agent_id=support_ag.id, tool_id=tool_objects["send_email"].id, is_allowed=True, can_read=True, can_write=True))
        db.add(AgentPermission(agent_id=support_ag.id, tool_id=tool_objects["refund_customer"].id, is_allowed=True, can_read=True, can_write=True, max_amount_limit=50000.0))
        db.add(AgentPermission(agent_id=support_ag.id, tool_id=tool_objects["execute_raw_sql"].id, is_allowed=False, can_read=False, can_write=False))

        # Sales Agent permissions
        db.add(AgentPermission(agent_id=sales_ag.id, tool_id=tool_objects["search_customer"].id, is_allowed=True, can_read=True, can_write=False))
        db.add(AgentPermission(agent_id=sales_ag.id, tool_id=tool_objects["send_email"].id, is_allowed=True, can_read=True, can_write=True))
        db.add(AgentPermission(agent_id=sales_ag.id, tool_id=tool_objects["refund_customer"].id, is_allowed=False, can_read=False, can_write=False))

        # Dev Agent permissions
        db.add(AgentPermission(agent_id=dev_ag.id, tool_id=tool_objects["github_create_issue"].id, is_allowed=True, can_read=True, can_write=True))
        db.add(AgentPermission(agent_id=dev_ag.id, tool_id=tool_objects["send_slack_alert"].id, is_allowed=True, can_read=True, can_write=True))
        db.add(AgentPermission(agent_id=dev_ag.id, tool_id=tool_objects["execute_raw_sql"].id, is_allowed=False, can_read=False, can_write=False))
        db.commit()

        # 6. Policies
        p1 = Policy(
            org_id=org.id,
            title="Max Refund Threshold Guard",
            category="Financial",
            description="Escalates refunds exceeding ₹50,000 for human security officer review.",
            rule_type="THRESHOLD",
            content="50000",
            action_on_trigger="ESCALATE",
            risk_score_weight=50,
            is_active=True
        )
        p2 = Policy(
            org_id=org.id,
            title="Prompt Injection & Jailbreak Prevention",
            category="Security",
            description="Blocks requests matching prompt override and jailbreak patterns.",
            rule_type="KEYWORDS",
            content="ignore instructions, drop table, jailbreak, dev mode",
            action_on_trigger="BLOCK",
            risk_score_weight=85,
            is_active=True
        )
        p3 = Policy(
            org_id=org.id,
            title="Strict Database Mutation Shield",
            category="Compliance",
            description="Blocks any raw SQL execution attempted by autonomous agents.",
            rule_type="KEYWORDS",
            content="execute_raw_sql, drop table, truncate",
            action_on_trigger="BLOCK",
            risk_score_weight=90,
            is_active=True
        )
        db.add_all([p1, p2, p3])
        db.commit()

        # 7. Sample Executions & Escalations
        e1 = Execution(
            id="exec_89dfa101",
            org_id=org.id,
            agent_id=support_ag.id,
            tool_name="search_customer",
            tool_input={"query": "john@acme.com"},
            decision="ALLOW",
            risk_score=5.0,
            risk_factors=[],
            execution_status="COMPLETED",
            output_data={"status": "success", "customer": {"name": "John Doe", "email": "john@acme.com"}},
            execution_time_ms=12.4
        )
        e2 = Execution(
            id="exec_89dfa102",
            org_id=org.id,
            agent_id=support_ag.id,
            tool_name="refund_customer",
            tool_input={"customer_id": "CUST_9921", "amount": 75000.0, "reason": "High-value refund request"},
            decision="ESCALATE",
            risk_score=65.0,
            risk_factors=["HIGH_VALUE_TRANSACTION: Refund amount ₹75,000.00 requires human verification"],
            execution_status="PENDING_APPROVAL",
            execution_time_ms=18.9
        )
        e3 = Execution(
            id="exec_89dfa103",
            org_id=org.id,
            agent_id=sales_ag.id,
            tool_name="refund_customer",
            tool_input={"customer_id": "CUST_1102", "amount": 1000.0},
            decision="BLOCK",
            risk_score=85.0,
            risk_factors=["UNAUTHORIZED_TOOL: Sales Agent does NOT have permission to invoke tool refund_customer"],
            execution_status="BLOCKED",
            execution_time_ms=8.1
        )
        db.add_all([e1, e2, e3])
        db.commit()

        # 8. Pending Approval for Escalated Execution e2
        app1 = Approval(
            org_id=org.id,
            execution_id="exec_89dfa102",
            agent_id=support_ag.id,
            tool_name="refund_customer",
            tool_input={"customer_id": "CUST_9921", "amount": 75000.0, "reason": "High-value refund request"},
            risk_score=65.0,
            status="PENDING"
        )
        db.add(app1)
        db.commit()

        # 9. Verification Record
        v1 = VerificationRecord(
            org_id=org.id,
            execution_id="exec_89dfa101",
            claim_text="Agent retrieved profile for john@acme.com.",
            expected_state={"email": "john@acme.com"},
            actual_state={"email": "john@acme.com"},
            confidence_score=1.0,
            status="VERIFIED"
        )
        db.add(v1)

        # 10. Security Event
        sec_ev = SecurityEvent(
            org_id=org.id,
            agent_id=sales_ag.id,
            event_type="UNAUTHORIZED_TOOL",
            severity="HIGH",
            details={"agent": "agent_sales_002", "attempted_tool": "refund_customer"},
            blocked=True
        )
        db.add(sec_ev)

        # 11. Initial Audit Log
        audit = AuditLog(
            org_id=org.id,
            actor="system",
            action="SEED_DATABASE",
            resource_type="System",
            resource_id="0",
            details={"status": "seeded"}
        )
        db.add(audit)
        db.commit()

        print("Database seed complete!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
