import os
from typing import Optional

class Config:
    # JSON file path for suppressed emails data
    SUPPRESSED_EMAILS_JSON_PATH: str = os.getenv(
        "SUPPRESSED_EMAILS_JSON_PATH", 
        "suppressed_emails.json"
    )
    
    # Ollama configuration
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # API configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

config = Config()
