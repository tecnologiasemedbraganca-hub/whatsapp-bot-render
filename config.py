import os

DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
PORT = int(os.environ.get("PORT", 10000))

