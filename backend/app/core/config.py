import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentShield"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "agentshield_super_secret_jwt_key_2026_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database (SQLite by default for local, PostgreSQL ready)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agentshield.db")

    class Config:
        case_sensitive = True

settings = Settings()
