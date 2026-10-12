import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""

os.environ.setdefault("GOOGLE_API_KEY", GOOGLE_API_KEY)

APP_NAME = os.getenv("APP_NAME", "qa_agent_app")
MODEL_NAME = os.getenv("MODEL_NAME") or "gemini-3.8-flash"
