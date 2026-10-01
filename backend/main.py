import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from seed_data import seed_db

# Import Routers
from app.api.endpoints import (
    auth,
    agents,
    tools,
    permissions,
    gateway,
    policies,
    approvals,
    verification,
    events,
    audit,
    analytics,
    agents_demo
)
from app.mcp import server as mcp_server
from app.orchestration.graph import sentinel_graph
from app.core.langfuse_tracer import langfuse_tracer

# Initialize DB
Base.metadata.create_all(bind=engine)
try:
    seed_db()
except Exception as e:
    print(f"Seed DB note: {e}")

app = FastAPI(
    title="Sentinel / AgentShield Security & Compliance Gateway",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["Agents Identity"])
app.include_router(tools.router, prefix=f"{settings.API_V1_STR}/tools", tags=["Tools Registry"])
app.include_router(permissions.router, prefix=f"{settings.API_V1_STR}/permissions", tags=["Permissions Matrix"])
app.include_router(gateway.router, prefix=f"{settings.API_V1_STR}/gateway", tags=["Security Gateway"])
app.include_router(gateway.router, prefix="/v1", tags=["V1 Gateway Compatibility"])
app.include_router(policies.router, prefix=f"{settings.API_V1_STR}/policies", tags=["Policy Engine"])
app.include_router(approvals.router, prefix=f"{settings.API_V1_STR}/approvals", tags=["Human Approvals"])
app.include_router(verification.router, prefix=f"{settings.API_V1_STR}/verification", tags=["Verification Engine"])
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/events", tags=["Security Events"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["Audit Logs"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Dashboard Analytics"])
app.include_router(agents_demo.router, prefix=f"{settings.API_V1_STR}/agents-demo", tags=["AI Agent Simulator"])

# Include MCP (Model Context Protocol) Endpoint Router
app.include_router(mcp_server.router, prefix="/mcp", tags=["Model Context Protocol (MCP)"])

# LangGraph Multi-Agent Orchestration Route
@app.post(f"{settings.API_V1_STR}/orchestration/run", tags=["LangGraph Multi-Agent"])
def run_orchestration_pipeline(agent_id: str, tool_name: str, payload: dict):
    state = sentinel_graph.run_pipeline(agent_id, tool_name, payload)
    langfuse_tracer.trace_agent_step(
        trace_id=f"tr_{agent_id}_{int(asyncio.get_event_loop().time())}",
        agent_id=agent_id,
        tool_name=tool_name,
        input_payload=payload,
        decision="ALLOW" if state["trust_score"] >= 70 else "FLAGGED",
        risk_score=state["risk_score"],
        verification_status=state["verification_status"]
    )
    return state

# WebSocket Stream
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Sentinel / AgentShield AI Compliance & Risk Auditor",
        "version": settings.VERSION,
        "mcp_endpoint": "/mcp/jsonrpc",
        "docs_url": "/docs",
        "gateway_endpoint": "/v1/tool/execute"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
