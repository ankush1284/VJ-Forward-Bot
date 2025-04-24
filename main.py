import asyncio
from config import Config
from pyrogram import Client, idle

if __name__ == "__main__":
    VJBot = Client(
        "VJ-Forward-Bot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        plugins=dict(root="plugins")
    )

    async def main():
        await VJBot.start()
        print("Bot Started.")
        await idle()

    asyncio.run(main())
