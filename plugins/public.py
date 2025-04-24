# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import asyncio 
from .utils import STS
from database import Db, db
from config import temp 
from script import Script
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait 
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# --- Caption Preset import ---
from plugins.caption_manager import apply_caption_rules

# --- Thumbnail Preset import ---
from plugins.thumbnail_enforcer import (
    is_valid_thumbnail, save_user_thumbnail, get_user_thumbnail, delete_user_thumbnail
)

def main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Caption Preset", callback_data="caption_preset")],
        [InlineKeyboardButton("🖼️ Thumbnail Preset", callback_data="thumbnail_preset")],
        # ... add your other settings buttons here ...
    ])

@Client.on_message(filters.private & filters.command(["forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
      _bot = await db.get_userbot(user_id)
      if not _bot:
          return await message.reply("<code>You didn't added any bot. Please add a bot using /settings !</code>")
    channels = await db.get_user_channels(user_id)
    if not channels:
       return await message.reply_text("please set a to channel in /settings before forwarding")
    if len(channels) > 1:
       for channel in channels:
          buttons.append([KeyboardButton(f"{channel['title']}")])
          btn_data[channel['title']] = channel['chat_id']
       buttons.append([KeyboardButton("cancel")]) 
       _toid = await bot.ask(message.chat.id, Script.TO_MSG.format(_bot['name'], _bot['username']), reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
       if _toid.text.startswith(('/', 'cancel')):
          return await message.reply_text(Script.CANCEL, reply_markup=ReplyKeyboardRemove())
       to_title = _toid.text
       toid = btn_data.get(to_title)
       if not toid:
          return await message.reply_text("wrong channel choosen !", reply_markup=ReplyKeyboardRemove())
    else:
       toid = channels[0]['chat_id']
       to_title = channels[0]['title']
    fromid = await bot.ask(message.chat.id, Script.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return 
    if fromid.text and not fromid.forward_date:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif fromid.forward_from_chat.type in [enums.ChatType.CHANNEL, 'supergroup']:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if last_msg_id == None:
           return await message.reply_text("**This may be a forwarded message from a group and sended by anonymous admin. instead of this please send last message link from group**")
    else:
        await message.reply_text("**invalid !**")
        return 
    try:
        title = (await bot.get_chat(chat_id)).title
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "private" if fromid.text else fromid.forward_from_chat.title
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    skipno = await bot.ask(message.chat.id, Script.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return
    forward_id = f"{user_id}-{skipno.id}"
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Script.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id))

# --- Caption Preset Handlers ---

@Client.on_callback_query(filters.regex(r'^caption_preset$'))
async def caption_preset_menu(bot, query):
    user_id = query.from_user.id
    user_config = await db.get_configs(user_id)
    caption_settings = user_config.get("caption_settings", {})
    text = (
        "<b>📝 Caption Preset</b>\n\n"
        f"<b>Status:</b> {'ON' if caption_settings.get('mode', 'on') == 'on' else 'OFF'}\n"
        f"<b>Add Text:</b> {caption_settings.get('add_text', 'None')}\n"
        f"<b>Replace:</b> {caption_settings.get('replace_dict', {})}\n"
        f"<b>Delete Caption:</b> {'Yes' if caption_settings.get('delete', False) else 'No'}\n"
        "\nChoose what you want to edit:"
    )
    buttons = [
        [InlineKeyboardButton("➕ Add Text", callback_data="caption_addtext")],
        [InlineKeyboardButton("🔁 Replace", callback_data="caption_replace")],
        [InlineKeyboardButton("🚫 Delete", callback_data="caption_delete")],
        [InlineKeyboardButton("🟢 On", callback_data="caption_on"),
         InlineKeyboardButton("🔴 Off", callback_data="caption_off")],
        [InlineKeyboardButton("⬅️ Back", callback_data="settings#main")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'^caption_addtext$'))
async def caption_addtext(bot, query):
    await query.message.edit("Send me the text you want to add to every caption:")
    response = await bot.ask(query.from_user.id, "Please send the text to add to all captions.", timeout=60)
    user_id = query.from_user.id
    config = await db.get_configs(user_id)
    config.setdefault("caption_settings", {})["add_text"] = response.text
    await db.update_configs(user_id, config)
    await response.reply("✅ Added text to caption.")
    await caption_preset_menu(bot, query)

@Client.on_callback_query(filters.regex(r'^caption_replace$'))
async def caption_replace(bot, query):
    await query.message.edit("Send replacements in the format:\n<code>old1:new1,old2:new2</code>")
    response = await bot.ask(query.from_user.id, "Send replacements in the format:\n<code>old1:new1,old2:new2</code>", timeout=120)
    user_id = query.from_user.id
    config = await db.get_configs(user_id)
    replace_dict = {}
    for pair in response.text.split(","):
        if ":" in pair:
            old, new = pair.split(":", 1)
            replace_dict[old.strip()] = new.strip()
    config.setdefault("caption_settings", {})["replace_dict"] = replace_dict
    await db.update_configs(user_id, config)
    await response.reply("✅ Replacement rules saved.")
    await caption_preset_menu(bot, query)

@Client.on_callback_query(filters.regex(r'^caption_delete$'))
async def caption_delete(bot, query):
    user_id = query.from_user.id
    config = await db.get_configs(user_id)
    config.setdefault("caption_settings", {})["delete"] = True
    await db.update_configs(user_id, config)
    await query.answer("Caption will be deleted.")
    await caption_preset_menu(bot, query)

@Client.on_callback_query(filters.regex(r'^caption_on$'))
async def caption_on(bot, query):
    user_id = query.from_user.id
    config = await db.get_configs(user_id)
    config.setdefault("caption_settings", {})["mode"] = "on"
    config["caption_settings"]["delete"] = False
    await db.update_configs(user_id, config)
    await query.answer("Caption ON.")
    await caption_preset_menu(bot, query)

@Client.on_callback_query(filters.regex(r'^caption_off$'))
async def caption_off(bot, query):
    user_id = query.from_user.id
    config = await db.get_configs(user_id)
    config.setdefault("caption_settings", {})["mode"] = "off"
    config["caption_settings"]["delete"] = False
    await db.update_configs(user_id, config)
    await query.answer("Caption OFF.")
    await caption_preset_menu(bot, query)

# --- Thumbnail Preset Handlers ---

@Client.on_callback_query(filters.regex(r'^thumbnail_preset$'))
async def thumbnail_preset_menu(bot, query):
    user_id = query.from_user.id
    data = await db.get_configs(user_id)
    thumb_id = data.get('thumbnail_file_id')
    thumb_status = "ON" if thumb_id else "OFF"
    text = (
        f"<b>🖼️ Thumbnail Preset</b>\n\n"
        f"<b>Status:</b> {thumb_status}\n"
        f"\nChoose an option:"
    )
    buttons = [
        [InlineKeyboardButton("🟢 Enable/Change", callback_data="thumbnail_enable")],
        [InlineKeyboardButton("🔴 Disable", callback_data="thumbnail_disable")],
        [InlineKeyboardButton("⬅️ Back", callback_data="settings#main")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'^thumbnail_enable$'))
async def thumbnail_enable(bot, query):
    await query.message.edit("Please send me the photo you want as your thumbnail (from your gallery):")
    response = await bot.ask(query.from_user.id, "Send a photo from your gallery to set as thumbnail.", timeout=120)
    if not is_valid_thumbnail(response):
        await response.reply("❌ Invalid thumbnail. Please send a photo or image document.")
        return
    file_id = response.photo.file_id if response.photo else response.document.file_id
    await save_user_thumbnail(query.from_user.id, file_id)
    await response.reply("✅ Thumbnail set successfully!")
    await thumbnail_preset_menu(bot, query)

@Client.on_callback_query(filters.regex(r'^thumbnail_disable$'))
async def thumbnail_disable(bot, query):
    await delete_user_thumbnail(query.from_user.id)
    await query.answer("Thumbnail feature disabled.")
    await thumbnail_preset_menu(bot, query)

# --- When forwarding/copying, apply the preset ---
# Example usage in your copy/forward logic:
# user_config = await db.get_configs(user_id)
# caption_settings = user_config.get("caption_settings", {})
# new_caption = apply_caption_rules(
#     original_caption=msg.caption,
#     mode=caption_settings.get("mode", "on"),
#     add_text=caption_settings.get("add_text", ""),
#     replace_dict=caption_settings.get("replace_dict", {}),
#     delete=caption_settings.get("delete", False)
# )
# Use new_caption as the caption when sending or copying messages.
#
# For thumbnails (video, document, PDF, etc.):
# thumb_id = await get_user_thumbnail(user_id)
# send_kwargs = dict(chat_id=target_chat_id, caption=new_caption)
# if thumb_id:
#     send_kwargs['thumb'] = thumb_id
# await bot.send_document(document=file_id, **send_kwargs)
# await bot.send_video(video=file_id, **send_kwargs)
# ...etc.

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01 
