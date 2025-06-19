import asyncio
import random
from Venom import VenomX
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message
from pyrogram.errors import ChannelPrivate
from config import EMOJIOS, IMG, STICKER, OWNER_ID, SUDO_IDS
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
from Venom.modules.chatbot import (
    chaton_text,
    chaton_sticker,
    remove_sticker_replies,
    remove_message_replies,
    clear_all_replies,
    remove_specific_reply,
)
from Abg.chat_status import adminsOnly

# Authorized users for restricted commands
AUTHORIZED_USERS = set([OWNER_ID] + SUDO_IDS)

@VenomX.on_cmd(["start", "aistart"])
async def start(_, m: Message):
    """Handle /start and /aistart commands."""
    try:
        if m.chat.type == ChatType.PRIVATE:
            emoji = random.choice(EMOJIOS)
            sticker = random.choice(STICKER)
            img = random.choice(IMG)

            # Combined animation sequence
            msg = await m.reply_text(f"{emoji} __ᴅιиg ᴅσиg ꨄ︎ ѕтαятιиg..__")
            await asyncio.sleep(0.2)
            await msg.edit(f"{emoji} __ᴅιиg ᴅσиg ꨄ sтαятιиg.....__")
            await msg.delete()

            # Brief sticker display
            umm = await m.reply_sticker(sticker)
            await asyncio.sleep(1)
            await umm.delete()

            # Final response
            await m.reply_photo(
                photo=img,
                caption="""<blockquote>ʜᴇya ǫᴛ/ǫᴛᴀ 💞, ɪ'ᴍ {0} 💜</blockquote>\n──────────────\n<b>• ᴛʏᴘᴇ :</b> ᴀɪ-ʙᴀsᴇᴅ ᴄʜᴀᴛʙᴏᴛ\n<b>• ᴜsᴀɢᴇ :</b> /chatbot [ᴏɴ/ᴏғғ] ғᴏʀ ᴛᴇxᴛs ᴏʀ /schatbot [ᴏɴ/ᴏғғ] ғᴏʀ sᴛɪᴄᴋᴇʀs\n<b>• ɴᴏᴛᴇ :</b> ʜɪᴛ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ""".format(VenomX.name),
                reply_markup=InlineKeyboardMarkup(DEV_OP),
            )
            await add_served_user(m.from_user.id)
        else:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption="""<blockquote>ʜᴇʟʟᴏ, ɪ'ᴍ {0} ✨</blockquote>\n──────────────\n<b>• ᴛʏᴘᴇ :</b> ᴀɪ-ʙᴀsᴇᴅ ᴄʜᴀᴛʙᴏᴛ\n<b>• ɴᴏᴛᴇ :</b> ᴘʟᴇᴀsᴇ ᴜsᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs""".format(VenomX.name),
                reply_markup=InlineKeyboardMarkup(HELP_START),
            )
            await add_served_chat(m.chat.id)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("help")
async def help(_, m: Message):
    """Handle /help command."""
    try:
        if m.chat.type == ChatType.PRIVATE:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption="""<b><blockquote>ʜᴇʟᴘ ᴍᴇɴᴜ ᴀᴄᴛɪᴠᴀᴛᴇᴅ 📖</blockquote></b>\n──────────────\n<b>• ᴅᴇsᴄʀɪᴘᴛɪᴏɴ :</b> ᴇxᴘʟᴏʀᴇ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs\n<b>• ɴᴏᴛᴇ :</b> sᴇʟᴇᴄᴛ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ""",
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
            )
            await add_served_user(m.from_user.id)
        else:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption="""<b><blockquote>ʜᴇʟᴘ ᴍᴇɴᴜ ʀᴇǫᴜᴇsᴛᴇᴅ 📖</blockquote></b>\n──────────────\n<b>• ɴᴏᴛᴇ :</b> ᴘʟᴇᴀsᴇ ᴘᴍ ᴍᴇ ᴛᴏ ᴠɪᴇᴡ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs""",
                reply_markup=InlineKeyboardMarkup(HELP_BUTN),
            )
            await add_served_chat(m.chat.id)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("updates")
async def repo(_, m: Message):
    """Handle /updates command."""
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
    """Send welcome message to new chat members."""
    try:
        for _ in m.new_chat_members:
            await m.reply_photo(
                photo=random.choice(IMG),
                caption="""<b><blockquote>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴄʜᴀᴛ 🤝</blockquote></b>\n──────────────\n<b>• ɴᴀᴍᴇ :</b> {0}\n<b>• ɴᴏᴛᴇ :</b> ᴜsᴇ /start ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴍᴇ""".format(VenomX.name),
            )
    except ChannelPrivate:
        pass

@VenomX.on_cmd("broadcast")
async def broadcast_cmd(_, m: Message):
    """Handle /broadcast command for authorized users."""
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command.")
            return
        await broadcast_command(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chatbot_cmd(_, m: Message):
    """Handle /chatbot command."""
    try:
        await chaton_text(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("schatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def schatbot_cmd(_, m: Message):
    """Handle /schatbot command."""
    try:
        await chaton_sticker(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("rms", group_only=True)
async def rms_cmd(_, m: Message):
    """Handle /rms command."""
    try:
        await remove_sticker_replies(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("rmm", group_only=True)
async def rmm_cmd(_, m: Message):
    """Handle /rmm command."""
    try:
        await remove_message_replies(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("clear", group_only=True)
async def clear_cmd(_, m: Message):
    """Handle /clear command."""
    try:
        await clear_all_replies(VenomX, m)
    except ChannelPrivate:
        pass

@VenomX.on_cmd("rem", group_only=True)
async def rem_cmd(_, m: Message):
    """Handle /rem command."""
    try:
        await remove_specific_reply(VenomX, m)
    except ChannelPrivate:
        pass
