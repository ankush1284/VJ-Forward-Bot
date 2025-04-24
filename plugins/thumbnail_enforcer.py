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
    if getattr(message, "photo", None):
        return True
    elif getattr(message, "document", None) and getattr(message.document, "mime_type", "").startswith("image/"):
        return True
    return False

# Alias for compatibility with old code
def validate_thumbnail(message: Message) -> bool:
    return is_valid_thumbnail(message)
