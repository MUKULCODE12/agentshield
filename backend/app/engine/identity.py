from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import Agent
from app.core.security import hash_api_key

def authenticate_agent(db: Session, api_key: str = None, agent_key: str = None) -> Agent:
    """
    Authenticates an AI Agent by its API key (e.g. sk_live_...) or agent_key identifier.
    Returns the Agent model if valid and active.
    """
    if api_key:
        key_hash = hash_api_key(api_key)
        agent = db.query(Agent).filter(Agent.api_key_hash == key_hash).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Agent API Key"
            )
    elif agent_key:
        agent = db.query(Agent).filter(Agent.agent_key == agent_key).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_key}' not found in Agent Registry"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Agent Identity credentials (X-Agent-API-Key or agent_key required)"
        )

    if agent.status.upper() != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Agent '{agent.name}' is currently {agent.status}. Execution denied."
        )

    return agent
