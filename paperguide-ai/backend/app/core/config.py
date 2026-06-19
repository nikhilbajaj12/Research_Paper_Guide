"""Configuration and environment settings."""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # App
    APP_NAME: str = "PaperGuide AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: Literal["development", "staging", "production"] = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./paperguide.db"
    # For MVP: sqlite:///paperguide.db (local file)
    # For production: postgresql://user:password@localhost/paperguide

    # File Storage
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    MAX_PDF_SIZE_MB: int = 50
    ACCEPTED_FILE_FORMATS: list[str] = [".pdf", ".docx", ".zip"]

    # Paths
    DATA_DIR: str = "./data"
    GUIDELINES_DIR: str = "./data/guidelines"
    TEMP_DIR: str = "./temp"
    GENERATED_DIR: str = "./generated"
    PACKAGE_DIR: str = "./generated/packages"
    MAX_PACKAGE_SIZE_MB: int = 100

    # Defaults
    DEFAULT_CONFERENCE_ID: str = "neurips-2025"
    DEFAULT_PACKAGE_TYPE: str = "neurips_overleaf"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # CORS (for frontend)
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # AI / LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str = ""  # Optional: for Azure / proxies

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env variables not defined in the schema


# Global settings instance
settings = Settings()
