import os

class Config:
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    BOT_OWNER = int(os.environ.get("BOT_OWNER", "0"))  # Default to "0" to avoid ValueError
    DATABASE_URI = os.environ.get("DATABASE_URI", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "vj-forward-bot")

# This fixes the ImportError in your code
temp = {}
