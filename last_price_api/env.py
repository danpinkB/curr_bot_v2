import os
from dotenv import load_dotenv
load_dotenv()

RABBITMQ_DSN__CONSUMER = os.environ.get("RABBITMQ_DSN__CONSUMER")
RABBITMQ_QUE__CONSUMER = os.environ.get("RABBITMQ_QUE__CONSUMER")

RABBITMQ_DSN__SENDER = os.environ.get("RABBITMQ_DSN__SENDER")
RABBITMQ_QUE__SENDER = os.environ.get("RABBITMQ_QUE__SENDER")

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")

REDIS_DSN__PRICE = os.environ.get("REDIS_DSN__PRICE")

