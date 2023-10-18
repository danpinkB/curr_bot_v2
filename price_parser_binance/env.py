import os
from dotenv import load_dotenv
load_dotenv()

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")
REDIS_DSN__PRICE = os.environ.get("REDIS_DSN__PRICE")
RABBITMQ_DSN__SENDER = os.environ.get("RABBITMQ_DSN__SENDER")
RABBITMQ_QUE__SENDER = os.environ.get("RABBITMQ_QUE__SENDER")

