"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for the application."""

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # API Authentication
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "sk_track3_987654321")

    # Celery / Redis (structural — not required for deployment)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Application
    APP_NAME: str = "Call Center Compliance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Temp directory for audio files
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/audio_processing")


settings = Settings()
