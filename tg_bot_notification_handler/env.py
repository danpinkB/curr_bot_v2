import os
from dotenv import load_dotenv
load_dotenv()
RMQ_HOST = os.environ.get("RMQ_HOST")
RMQ_USER = os.environ.get("RMQ_USER")
RMQ_PASSWORD = os.environ.get("RMQ_PASSWORD")
RABBITMQ_QUE__CONSUMER = os.environ.get("RABBITMQ_QUE__CONSUMER")

TELEGRAM_BOT_PASSWORD = os.environ.get("TELEGRAM_BOT_PASSWORD")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")

DB_PATH = os.environ.get("DB_PATH")

