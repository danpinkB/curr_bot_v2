import os
from dotenv import load_dotenv
load_dotenv()

JSON_RPC_PROVIDER = os.environ.get("JSON_RPC_PROVIDER")
REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")
REDIS_DSN__PATH = os.environ.get("REDIS_DSN__PATH")
REDIS_DSN__PRICE = os.environ.get("REDIS_DSN__PRICE")
REDIS_DSN__SYNC = os.environ.get("REDIS_DSN__SYNC")
REDIS_DSN__INFO = os.environ.get("REDIS_DSN__INFO")


RABBITMQ_DSN__SENDER = os.environ.get("RABBITMQ_DSN__SENDER")
RABBITMQ_QUE__SENDER = os.environ.get("RABBITMQ_QUE__SENDER")

