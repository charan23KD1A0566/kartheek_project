import os
from pathlib import Path
from dotenv import load_dotenv

# Keep local and Streamlit Cloud configuration on the project-level .env.
# Existing environment variables (including cloud secrets) take precedence.
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "sif_sentinel")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")  # openai, anthropic, etc.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# Frontend API
FRONTEND_API_URL = os.getenv("FRONTEND_API_URL", "http://localhost:5173")

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")

# Security
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is required. Set it in backend/.env before starting the API."
    )
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Server
DEBUG = os.getenv("DEBUG", "True") == "True"
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Risk Engine Weights (Prototype)
RISK_ENGINE_CONFIG = {
    "hazard_severity_weight": 0.35,
    "exposure_weight": 0.25,
    "control_failure_weight": 0.30,
    "consequence_potential_weight": 0.10,
}

# Hazard Thresholds
CRITICAL_HAZARD_KEYWORDS = [
    "energized",
    "high voltage",
    "fatal",
    "death",
    "confined space",
    "rescue",
    "hazardous atmosphere",
    "oxygen",
    "suspended load",
    "fall",
    "unprotected edge",
]

print("[OK] Configuration loaded")
print(f"  MongoDB: {MONGODB_URI.replace(MONGODB_URI.split('@')[1] if '@' in MONGODB_URI else MONGODB_URI, '***') if '@' in MONGODB_URI else MONGODB_URI}")
print(f"  Database: {MONGODB_DATABASE}")
print(f"  LLM Provider: {LLM_PROVIDER if LLM_PROVIDER else 'RULE ENGINE FALLBACK'}")
print(f"  Debug: {DEBUG}")
