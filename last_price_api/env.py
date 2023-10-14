import os
from dotenv import load_dotenv
load_dotenv()

RMQ_HOST = os.environ.get("RMQ_HOST")
RMQ_USER = os.environ.get("RMQ_USER")
RMQ_PASSWORD = os.environ.get("RMQ_PASSWORD")
RABBITMQ_QUE__CONSUMER = os.environ.get("RABBITMQ_QUE__CONSUMER")
RABBITMQ_QUE__SENDER = os.environ.get("RABBITMQ_QUE__SENDER")

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")

REDIS_DSN__PRICE = os.environ.get("REDIS_DSN__PRICE")

