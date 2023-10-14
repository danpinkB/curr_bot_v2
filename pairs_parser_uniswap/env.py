import os
from dotenv import load_dotenv
load_dotenv()

REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")
REDIS_DSN__INFO = os.environ.get("REDIS_DSN__INFO")

