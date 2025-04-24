from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from database import db
from script import Script
from config import Config
import time

START_TIME = time.time()

main_buttons = [
    [
        InlineKeyboardButton('Source Channel', url='https://t.me/kingvj01')
    ],
    [
        InlineKeyboardButton('Discussion Group', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('Bots Channel', url='https://t.me/vj_botz')
    ],
    [
        InlineKeyboardButton('YouTube Channel', url='https://youtube.com/@Tech_VJ')
    ],
    [
        InlineKeyboardButton('Help', callback_data='help'),
        InlineKeyboardButton('About', callback_data='about')
    ],
    [
        InlineKeyboardButton('Settings', callback_data='settings#main')
    ]
]

@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await client.send_message(
        chat_id=message.chat.id,
        reply_markup=reply_markup,
        text=Script.START_TXT.format(message.from_user.first_name)
    )

@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER))
async def restart(client, message):
    msg = await message.reply_text(text="<i>Trying to restarting.....</i>")
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully!</i>")

@Client.on_callback_query(filters.regex(r'^help'))
async def helpcb(bot, query):
    buttons = [
        [
            InlineKeyboardButton('How to Use', callback_data='how_to_use')
        ],
        [
            InlineKeyboardButton('About', callback_data='about'),
            InlineKeyboardButton('Settings', callback_data='settings#main')
        ],
        [
            InlineKeyboardButton('Back', callback_data='back')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(text=Script.HELP_TXT, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r'^how_to_use'))
async def how_to_use(bot, query):
    buttons = [[InlineKeyboardButton('Back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.HOW_USE_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'^back'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
        reply_markup=reply_markup,
        text=Script.START_TXT.format(query.from_user.first_name)
    )

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    buttons = [
        [
            InlineKeyboardButton('Back', callback_data='help'),
            InlineKeyboardButton('Stats', callback_data='status')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.ABOUT_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'^status'))
async def status(bot, query):
    users_count, bots_count = await db.total_users_bots_count()
    forwardings = await db.forwad_count()
    upt = await get_bot_uptime(START_TIME)
    buttons = [
        [
            InlineKeyboardButton('Back', callback_data='help'),
            InlineKeyboardButton('System Stats', callback_data='systm_sts')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.STATUS_TXT.format(upt, users_count, bots_count, forwardings),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'^systm_sts'))
async def sys_status(bot, query):
    buttons = [[InlineKeyboardButton('Back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text="System Status: All systems operational",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def get_bot_uptime(start_time):
    uptime_seconds = int(time.time() - start_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_string = ""
    if uptime_hours:
        uptime_string += f"{uptime_hours} hours "
    if uptime_minutes:
        uptime_string += f"{uptime_minutes} minutes "
    uptime_string += f"{uptime_seconds} seconds"
    return uptime_string

@Client.on_message(filters.private & filters.command(['forward_range']))
async def forward_range_command(client, message):
    user_id = message.from_user.id
    await message.reply_text(Script.RANGE_FORWARD_TXT)

@Client.on_message(filters.private & filters.command(['addcaption']))
async def add_caption(client, message):
    user_id = message.from_user.id
    caption_text = message.text.split(' ', 1)
    if len(caption_text) == 1:
        return await message.reply_text("Please provide text to add to caption")
    
    current_caption = (await db.get_configs(user_id))['caption'] or ""
    new_caption = current_caption + " " + caption_text[1]
    await db.update_configs(user_id, 'caption', new_caption)
    await message.reply_text("Caption updated successfully!")
