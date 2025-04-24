# plugins/thumbnail_enforcer.py

from pyrogram.types import Message
from database import db  # Adjust import if needed

async def save_user_thumbnail(user_id: int, file_id: str):
    await db.update_configs(user_id, 'thumbnail_file_id', file_id)

async def get_user_thumbnail(user_id: int):
    data = await db.get_configs(user_id)
    return data.get('thumbnail_file_id')

async def delete_user_thumbnail(user_id: int):
    await db.update_configs(user_id, 'thumbnail_file_id', None)

def is_valid_thumbnail(message: Message) -> bool:
    if message.photo:
        return True
    elif message.document and message.document.mime_type.startswith("image/"):
        return True
    return False
