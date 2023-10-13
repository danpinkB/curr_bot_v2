import os
from dotenv import load_dotenv
load_dotenv()

JSON_RPC_PROVIDER = os.environ.get("JSON_RPC_PROVIDER")

UNI_CLI_PATH = os.environ.get("UNI_CLI_PATH")

PRICE_IMPACT_CALCULATION_VOLUME = int(os.environ.get("PRICE_IMPACT_CALCULATION_VOLUME"))
RESIDENT_SLEEPER_DELAY = float(os.environ.get("RESIDENT_SLEEPER_DELAY"))

SETTINGS_R_HOST = os.environ.get("SETTINGS_R_HOST")
SETTINGS_R_PASSWORD = os.environ.get("SETTINGS_R_PASSWORD")
SETTINGS_R_DB = os.environ.get("SETTINGS_R_DB")

PATH_R_HOST = os.environ.get("PATH_R_HOST")
PATH_R_PASSWORD = os.environ.get("PATH_R_PASSWORD")
PATH_R_DB = os.environ.get("PATH_R_DB")

SYNC_R_HOST = os.environ.get("SYNC_R_HOST")
SYNC_R_PASSWORD = os.environ.get("SYNC_R_PASSWORD")
SYNC_R_DB = os.environ.get("SYNC_R_DB")

INFO_R_HOST = os.environ.get("SYNC_R_HOST")
INFO_R_PASSWORD = os.environ.get("SYNC_R_PASSWORD")
INFO_R_DB = os.environ.get("SYNC_R_DB")