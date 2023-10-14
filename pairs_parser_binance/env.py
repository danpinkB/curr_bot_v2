import os
from dotenv import load_dotenv
load_dotenv()
BINANCE_API = os.environ.get("BINANCE_API")

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")
REDIS_DSN__INFO = os.environ.get("REDIS_DSN__INFO")