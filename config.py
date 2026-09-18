import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try: ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))
except ValueError: ALLOWED_USER_ID = 0
DB_PATH = str(BASE_DIR / "data" / "cryptograham.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MOBULA_API_KEY = os.getenv("MOBULA_API_KEY")
MOBULA_BASE_URL = os.getenv("MOBULA_BASE_URL", "https://api.mobula.io/api/2")
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "30"))
WATCH_INTERVAL_SECONDS = int(os.getenv("WATCH_INTERVAL_SECONDS", "60"))
