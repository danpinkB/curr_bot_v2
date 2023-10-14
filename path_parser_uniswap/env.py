import os
from dotenv import load_dotenv
load_dotenv()

JSON_RPC_PROVIDER = os.environ.get("JSON_RPC_PROVIDER")
UNI_CLI_PATH = os.environ.get("UNI_CLI_PATH")
REDIS_DSN__SETTINGS = os.environ.get("REDIS_DSN__SETTINGS")
REDIS_DSN__PATH = os.environ.get("REDIS_DSN__PATH")
REDIS_DSN__SYNC = os.environ.get("REDIS_DSN__SYNC")
REDIS_DSN__INFO = os.environ.get("REDIS_DSN__INFO")