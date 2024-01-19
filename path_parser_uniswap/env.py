import os
from dotenv import load_dotenv
load_dotenv()

JSON_RPC_PROVIDER = os.environ.get("JSON_RPC_PROVIDER")
UNI_CLI_PATH = os.environ.get("UNI_CLI_PATH")
PATH_DB__DSN = os.environ.get("PATH_DB__DSN")
SYNC_DB__DSN = os.environ.get("SYNC_DB__DSN")
