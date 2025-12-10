from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path


def find_env_file():
    """Find .env file in project root"""
    # Get the directory where this config file is located (backend/app/)
    current_file = Path(__file__).resolve()
    # Go up to project root (backend/app/ -> backend/ -> root)
    project_root = current_file.parent.parent.parent
    env_file = project_root / ".env"
    
    # Also try one level up (in case we're already at root)
    if not env_file.exists():
        env_file = current_file.parent.parent.parent / ".env"
    
    return str(env_file) if env_file.exists() else ".env"


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str

    # Backend
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    fernet_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Recognition
    similarity_threshold: float = 0.36

    # Admin Login
    admin_email: str = "admin@cyber.com"
    admin_password: str = "admin123"

    class Config:
        env_file = find_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


settings = Settings()
