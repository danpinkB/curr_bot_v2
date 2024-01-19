import os
from dotenv import load_dotenv
load_dotenv()
MESSAGE_BROKER_CONSUMER__DSN = os.environ.get("MESSAGE_BROKER_CONSUMER__DSN")
MESSAGE_BROKER_CONSUMER__QUE = os.environ.get("MESSAGE_BROKER_CONSUMER__QUE")

TELEGRAM_BOT_PASSWORD = os.environ.get("TELEGRAM_BOT_PASSWORD")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

SYNC_DB__DSN  = os.environ.get("SYNC_DB__DSN")
SETTINGS_DB__DSN = os.environ.get("SETTINGS_DB__DSN")

DB_PATH = os.environ.get("DB_PATH")

