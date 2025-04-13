import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3-8b-8192")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")