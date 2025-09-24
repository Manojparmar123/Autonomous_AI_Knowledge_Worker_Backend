# apps/backend/app/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # --- Environment ---
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # --- Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    # --- Databases ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # --- Storage ---
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ai-worker")
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")

    # --- Mail ---
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@example.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "AI Worker")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() in ("true", "1", "yes")
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() in ("true", "1", "yes")

    # --- Integrations ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY")
    ALPHAVANTAGE_KEY: str = os.getenv("ALPHAVANTAGE_KEY")
    GOOGLE_CX: str = os.getenv("GOOGLE_CX")
    GOOGLE_KEY: str = os.getenv("GOOGLE_KEY")
    ALPHA_KEY: str = os.getenv("ALPHA_KEY")
    CX_ID: str = os.getenv("CX_ID")

    # --- Pinecone / HuggingFace embeddings ---
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "ai-worker-chunks")
    HF_INDEX_NAME: str = os.getenv("HF_INDEX_NAME", "huggingface-index")
    GEN_AI_INDEX: str = os.getenv("GEN_AI_INDEX", "gemini-index")
    HF_EMBED_MODEL: str = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    class Config:
        env_file = ".env"
        extra = "ignore"


# Single shared instance
settings = Settings()

# Direct import shortcuts (optional but useful)
APP_ENV = settings.APP_ENV
APP_BASE_URL = settings.APP_BASE_URL
FRONTEND_URL = settings.FRONTEND_URL
JWT_SECRET = settings.JWT_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
MAIL_USERNAME = settings.MAIL_USERNAME
MAIL_FROM = settings.MAIL_FROM
