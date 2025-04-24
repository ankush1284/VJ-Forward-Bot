from flask import Flask, request
from pyrogram import Client
import os
import threading
import asyncio

from config import Config

app = Flask(__name__)

# Initialize Pyrogram Client (bot)
bot = Client(
    "VJ-Forward-Bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    plugins=dict(root="plugins")
)

# Start the Pyrogram client in a background thread for webhook mode
def start_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot.run()

threading.Thread(target=start_bot, daemon=True).start()

@app.route('/')
def hello_world():
    return 'Hello from Koyeb!'

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    if update:
        bot.process_new_updates([update])
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
