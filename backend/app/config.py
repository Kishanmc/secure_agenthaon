import os
from pydantic_settings import BaseSettings
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "SecureAgent AI"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./secureagent.db"
    
    # API Keys
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # AI Config
    # Supports 'gemini', 'openai', 'mock'
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "gemini-1.5-flash"
    
    # GitHub Config
    GITHUB_TOKEN: str = ""
    
    # Paths
    DATA_DIR: str = str(BASE_DIR / "data")
    CLONE_DIR: str = str(BASE_DIR / "data" / "clones")
    CHROMA_DIR: str = str(BASE_DIR / "data" / "chroma")
    
    # Webhook secret (optional validation)
    GITHUB_WEBHOOK_SECRET: str = "secureagent_secret_12345"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Load settings and configure defaults based on what keys are present
settings = Settings()

# Auto-detect AI Provider if configured to "mock" but keys exist
if settings.AI_PROVIDER == "mock" or not settings.AI_PROVIDER:
    if os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY:
        settings.AI_PROVIDER = "gemini"
    elif os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY:
        settings.AI_PROVIDER = "openai"
    else:
        settings.AI_PROVIDER = "mock"

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.CLONE_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
