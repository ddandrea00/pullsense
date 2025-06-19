import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple settings management - we'll expand this as needed"""
    
    # OpenAI settings - we'll need this soon
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pullsense.db")
    
    # Add JWT_SECRET if not already there:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    
    # Redis URL for when we add Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Settings
    API_TITLE = "PullSense API"
    API_VERSION = "0.2.0"
    
settings = Settings()

