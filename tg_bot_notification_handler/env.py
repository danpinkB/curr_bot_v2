import os
from dotenv import load_dotenv
load_dotenv()
RABBITMQ_DSN__CONSUMER = os.environ.get("RABBITMQ_DSN__CONSUMER")
RABBITMQ_QUE__CONSUMER = os.environ.get("RABBITMQ_QUE__CONSUMER")

TELEGRAM_BOT_PASSWORD = os.environ.get("TELEGRAM_BOT_PASSWORD")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

REDIS_DSN__SYNC  = os.environ.get("REDIS_DSN__SYNC")
REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")

DB_PATH = os.environ.get("DB_PATH")

