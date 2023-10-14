import os
from dotenv import load_dotenv
load_dotenv()

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")

REDIS_DSN__PRICE = os.environ.get("REDIS_DSN__PRICE")

MANAGEMENT_API_PORT = os.environ.get("MANAGEMENT_API_PORT")
