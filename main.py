from pyrogram import Client
from plugins import *
from config import *

app = Client("forwardbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Load all plugin handlers
import plugins.broadcast
import plugins.commands
import plugins.db
import plugins.public
import plugins.regix
import plugins.settings
import plugins.test
import plugins.unequeify
import plugins.utils

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()  # This ensures the bot starts and keeps listening
