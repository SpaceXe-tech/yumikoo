import asyncio
import random

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message
from pyrogram.errors import ChannelPrivate

from config import EMOJIOS, IMG, STICKER
from Venom import VenomX, config
from Venom.database.chats import add_served_chat
from Venom.database.users import add_served_user
from Venom.modules.helpers import (
    CLOSE_BTN,
    DEV_OP,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    HELP_START,
    SOURCE_READ,
    START,
)
from Venom.modules.broadcast import broadcast_command

# Authorized users for restricted commands
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

@VenomX.on_cmd(["start", "aistart"])
async def start(_, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        accha = await m.reply_text(
            text=random.choice(EMOJIOS),
        )
        await asyncio.sleep(1.3)
        await accha.edit("__ᴅιиg ᴅσиg ꨄ︎ ѕтαятιиg..__")
        await asyncio.sleep(0.2)
        await accha.edit("__ᴅιиg ᴅσиg ꨄ sтαятιиg.....__")
        await asyncio.sleep(0.2)
        await accha.edit("__ᴅιиg ᴅσиg ꨄ︎ sтαятιиg..__")
        await asyncio.sleep(0.2)
        await accha.delete()
        try:
            umm = await m.reply_sticker(sticker=random.choice(STICKER))
            await asyncio.sleep(2)
            await umm.delete()
        except ChannelPrivate:
            pass  # Skip if chat is inaccessible
        try:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption=f"""**๏ ʜᴏʟᴀ ᴀᴍɪɢᴏ ʙᴀʙʏ 💟 ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ?, ɪ ᴀᴍ {VenomX.name}**\n**➻ ᴀɴ ᴀɪ ʙᴀsᴇᴅ ᴄʜᴀᴛʙᴏᴛ .**\n**──────────────**\n**➻ ᴜsᴀɢᴇ /chatbot [ᴏɴ/ᴏғғ]**\n<b>||๏ ʜɪᴛ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ғᴏʀ ʜᴇʟᴘ||</b>""",
                reply_markup=InlineKeyboardMarkup(DEV_OP),
            )
            await add_served_user(m.from_user.id)
        except ChannelPrivate:
            pass  # Skip if chat is inaccessible
    else:
        try:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption=START,
                reply_markup=InlineKeyboardMarkup(HELP_START),
            )
            await add_served_chat(m.chat.id)
        except ChannelPrivate:
            pass  # Skip if chat is inaccessible

@VenomX.on_cmd("help")
async def help(client: VenomX, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        try:
            hmm = await m.reply_photo(
                photo=random.choice(IMG),
                caption=HELP_READ,
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
            )
            await add_served_user(m.from_user.id)
        except ChannelPrivate:
            pass
    else:
        try:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption="**ʜᴇʏ, ᴘʟᴇᴀsᴇ 🥺 ᴘᴍ ᴍᴇ ғᴏʀ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs!**",
                reply_markup=InlineKeyboardMarkup(HELP_BUTN),
            )
            await add_served_chat(m.chat.id)
        except ChannelPrivate:
            pass

@VenomX.on_cmd("updates")
async def repo(_, m: Message):
    try:
        await m.reply_text(
            text=SOURCE_READ,
            reply_markup=InlineKeyboardMarkup(CLOSE_BTN),
            disable_web_page_preview=True,
        )
    except ChannelPrivate:
        pass

@VenomX.on_message(filters.new_chat_members)
async def welcome(_, m: Message):
    for member in m.new_chat_members:
        try:
            await m.reply_photo(photo=random.choice(IMG), caption=START)
        except ChannelPrivate:
            pass

# Register broadcast command
@VenomX.on_message(filters.command("broadcast"))
async def broadcast(_, m: Message):
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /broadcast.")
        return
    await broadcast_command(VenomX, m)
