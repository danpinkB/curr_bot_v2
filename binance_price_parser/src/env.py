import os
from dotenv import load_dotenv
load_dotenv()

SETTINGS_R_HOST = os.environ.get("SETTINGS_R_HOST")
SETTINGS_R_PASSWORD = os.environ.get("SETTINGS_R_PASSWORD")
SETTINGS_R_DB = os.environ.get("SETTINGS_R_DB")

SENDER_RMQ_HOST = os.environ.get("SENDER_RMQ_HOST")
SENDER_RMQ_USER = os.environ.get("SENDER_RMQ_USER")
SENDER_RMQ_PASSWORD = os.environ.get("SENDER_RMQ_PASSWORD")
SENDER_RMQ_QUE = os.environ.get("SENDER_RMQ_QUE")