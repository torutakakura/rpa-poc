"""Configuration settings for RPA Backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "55432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "rpa")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rpa_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rpa")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_SUMMARY_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", OPENAI_MODEL)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# MCP configuration
MCP_SERVER_URL = (
    os.getenv("MCP_SERVER_URL")
    or os.getenv("MCP_HTTP_SERVER_URL")
    or "http://localhost:8080/mcp"
)

# Path configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = Path(__file__).resolve().parent
STEP_SCHEMA_DOC = PROJECT_ROOT / "docs" / "ashirobo-step-list-schema.md"
STEP_LIST_PATH = BACKEND_ROOT / "generated_step_list.json"
MCP_MAIN_PATH = PROJECT_ROOT / "rpa-mcp" / "main.py"

# Log configuration
LOG_DIR = BACKEND_ROOT / "logs"
STEP1_LOG_PATH = LOG_DIR / "step1.log"
STEP2_LOG_PATH = LOG_DIR / "step2.log"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

