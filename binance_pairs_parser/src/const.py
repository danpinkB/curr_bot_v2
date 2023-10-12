import os
from dotenv import load_dotenv
load_dotenv()

RESIDENT_SLEEPER_DELAY = float(os.environ.get("RESIDENT_SLEEPER_DELAY"))

BINANCE_API = os.environ.get("BINANCE_API")

SETTINGS_R_HOST = os.environ.get("SETTINGS_R_HOST")
SETTINGS_R_PASSWORD = os.environ.get("SETTINGS_R_PASSWORD")
SETTINGS_R_DB = os.environ.get("SETTINGS_R_DB")

INFO_R_HOST = os.environ.get("SYNC_R_HOST")
INFO_R_PASSWORD = os.environ.get("SYNC_R_PASSWORD")
INFO_R_DB = os.environ.get("SYNC_R_DB")

DAILY_RATE = int(os.environ.get("DAILY_RATE"))