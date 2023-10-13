import os
from dotenv import load_dotenv
load_dotenv()
MANAGEMENT_API_URI = os.environ.get("MANAGEMENT_API_URI")
MANAGEMENT_API_PORT = os.environ.get("MANAGEMENT_API_PORT")

TELEGRAM_BOT_PASSWORD = os.environ.get("TELEGRAM_BOT_PASSWORD")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

DB_PATH = os.environ.get("DB_PATH")