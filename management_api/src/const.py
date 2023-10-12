import os
from dotenv import load_dotenv
load_dotenv()

SETTINGS_R_HOST = os.environ.get("SETTINGS_R_HOST")
SETTINGS_R_PASSWORD = os.environ.get("SETTINGS_R_PASSWORD")
SETTINGS_R_DB = os.environ.get("SETTINGS_R_DB")

PRICE_R_HOST = os.environ.get("SETTINGS_R_HOST")
PRICE_R_PASSWORD = os.environ.get("SETTINGS_R_PASSWORD")
PRICE_R_DB = os.environ.get("SETTINGS_R_DB")

MANAGEMENT_API_PORT = os.environ.get("MANAGEMENT_API_PORT")
