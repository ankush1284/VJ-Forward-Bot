import threading
from flask import Flask
from pyrogram import Client
from config import Config

# Flask app for health check or status page
app = Flask(__name__)

@app.route('/')
def home():
    return "VJ Forward Bot is running!"

def run_flask():
    # Use 0.0.0.0 to accept external connections if needed
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Pyrogram bot in the main thread (this is REQUIRED)
    bot = Client(
        "my_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins")
    )
    bot.run()
