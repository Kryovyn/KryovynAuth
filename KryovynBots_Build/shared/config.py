import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "").strip()
API_TOKEN = os.getenv("API_TOKEN", "").strip()

TG_TOKEN = os.getenv("TG_TOKEN", "").strip()
TG_PROXY = os.getenv("TG_PROXY", "").strip()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID", "").strip()
DS_PROXY = os.getenv("DS_PROXY", "").strip()
