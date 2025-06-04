import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple settings management - we'll expand this as needed"""
    
    # OpenAI settings - we'll need this soon
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Database - default to SQLite
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pullsense.db")
    
    # Redis URL for when we add Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Settings
    API_TITLE = "PullSense API"
    API_VERSION = "0.2.0"

settings = Settings()

