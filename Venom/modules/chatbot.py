import random
from Abg.chat_status import adminsOnly
from pymongo import MongoClient
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from config import MONGO_URL, OWNER_ID, SUDO_IDS
from Venom import VenomX
from Venom.modules.helpers import CHATBOT_ON, is_admins
import os
import re

# Authorized users for restricted commands
AUTHORIZED_USERS = set([OWNER_ID] + SUDO_IDS)

# Cache for learned replies (in-memory)
REPLY_CACHE = {
    "text": {},  # {word: [(reply_text, check_type), ...]}
    "sticker": {}  # {sticker_id: [(reply_text, check_type), ...]}
}

# Load slang words from slang.txt
SLANG_FILE = os.path.join(os.path.dirname(__file__), "slang.txt")
SLANG_WORDS = set()
if os.path.exists(SLANG_FILE):
    with open(SLANG_FILE, "r", encoding="utf-8") as f:
        SLANG_WORDS = {word.strip().lower() for word in f if word.strip()}

def is_slang(text: str) -> bool:
    """Check if text contains any slang words."""
    if not text:
        return False
    words = re.split(r'\s+|[^\w\s]', text.lower())
    return any(word in SLANG_WORDS for word in words if word)

def load_cache():
    """Load replies from MongoDB into cache at startup."""
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        for doc in chatai.find():
            word = doc.get("word")
            reply_text = doc.get("text")
            check_type = doc.get("check")
            if word and reply_text:
                if check_type == "sticker":
                    REPLY_CACHE["sticker"].setdefault(word, []).append((reply_text, check_type))
                else:
                    REPLY_CACHE["text"].setdefault(word, []).append((reply_text, check_type))
    finally:
        chatdb.close()

# Load cache on startup
load_cache()

@VenomX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_text(_, m: Message):
    """Enable/disable text-based chatbot."""
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ʏᴜᴋɪᴛᴀ💐 ᴛᴇxᴛ ᴄʜᴀᴛ-ʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

@VenomX.on_cmd("schatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_sticker(_, m: Message):
    """Enable/disable sticker-based chatbot."""
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ʏᴜᴋɪᴛᴀ💐 sᴛɪᴄᴋᴇʀ ᴄʜᴀᴛ-ʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

@VenomX.on_cmd("rms", group_only=True)
async def remove_sticker_replies(_: Client, m: Message):
    """Remove all learned sticker replies."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": "sticker"}).deleted_count
        REPLY_CACHE["sticker"].clear()  # Clear sticker cache
        await m.reply_text(f"Rᴇᴍᴏᴠᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ sᴛɪᴄᴋᴇʀ ʀᴇᴘʟɪᴇs.")
    finally:
        chatdb.close()

@VenomX.on_cmd("rmm", group_only=True)
async def remove_message_replies(_: Client, m: Message):
    """Remove all learned text message replies."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": {"$in": ["text", "none"]}}).deleted_count
        REPLY_CACHE["text"].clear()  # Clear text cache
        await m.reply_text(f"ᴠᴀɴɪsʜᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇs.")
    finally:
        chatdb.close()

@VenomX.on_cmd("clear", group_only=True)
async def clear_all_replies(_: Client, m: Message):
    """Remove all learned replies."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({}).deleted_count
        REPLY_CACHE["text"].clear()
        REPLY_CACHE["sticker"].clear()
        await m.reply_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ 🍃 ᴠᴀɴɪsʜᴇᴅ ᴀʟʟ {deleted} ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟɪᴇs.")
    finally:
        chatdb.close()

@VenomX.on_cmd("rem", group_only=True)
async def remove_specific_reply(_: Client, m: Message):
    """Remove a specific learned reply."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    if not m.reply_to_message:
        await m.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ.")
        return
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        deleted = 0
        if m.reply_to_message.text:
            # Remove from DB
            deleted = chatai.delete_many({"text": m.reply_to_message.text, "check": {"$in": ["text", "none"]}}).deleted_count
            # Update cache
            for word, replies in list(REPLY_CACHE["text"].items()):
                REPLY_CACHE["text"][word] = [(r, t) for r, t in replies if r != m.reply_to_message.text]
                if not REPLY_CACHE["text"][word]:
                    del REPLY_CACHE["text"][word]
        elif m.reply_to_message.sticker:
            # Remove from DB
            deleted = chatai.delete_many({"text": m.reply_to_message.sticker.file_id, "check": "sticker"}).deleted_count
            # Update cache
            for word, replies in list(REPLY_CACHE["sticker"].items()):
                REPLY_CACHE["sticker"][word] = [(r, t) for r, t in replies if r != m.reply_to_message.sticker.file_id]
                if not REPLY_CACHE["sticker"][word]:
                    del REPLY_CACHE["sticker"][word]
        else:
            await m.reply_text("Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ʀᴇᴍᴏᴠᴀʟ ᴛʏᴘᴇ. ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ.")
            return
        if deleted > 0:
            await m.reply_text("ᴠᴀɴɪsʜᴇᴅ ᴛʜᴇ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟʏ.")
        else:
            await m.reply_text("ɴᴏ ᴍᴀᴛᴄʜɪɴɢ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟɪᴇs ғᴏᴜɴᴅ.")
    finally:
        chatdb.close()

@VenomX.on_message(
    filters.text & filters.group & ~filters.private & ~filters.bot & ~filters.command(["!", "/", "?", "@", "#"]), group=4
)
async def chatbot_text(client: Client, message: Message):
    """Handle text-based chatbot responses and learning."""
    chatdb = MongoClient(MONGO_URL)
    vickdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})

        if not is_vick:
            if not message.reply_to_message:
                # Respond with text replies from cache if /chatbot is enabled
                if message.text in REPLY_CACHE["text"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["text"][message.text] if t in ["text", "none"]]
                    if replies:
                        reply, check_type = random.choice(replies)
                        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                        await message.reply_text(reply)
            elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == client.me.id:
                # Respond with text replies from cache if /chatbot is enabled
                if message.text in REPLY_CACHE["text"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["text"][message.text] if t in ["text", "none"]]
                    if replies:
                        reply, check_type = random.choice(replies)
                        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                        await message.reply_text(reply)
            elif message.reply_to_message and message.reply_to_message.text:
                # Learn new reply (text or sticker)
                if message.sticker:
                    is_chat = chatai.find_one({"word": message.reply_to_message.text, "id": message.sticker.file_unique_id})
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.text,
                                "text": message.sticker.file_id,
                                "check": "sticker",
                                "id": message.sticker.file_unique_id,
                            }
                        )
                        REPLY_CACHE["text"].setdefault(message.reply_to_message.text, []).append((message.sticker.file_id, "sticker"))
                elif message.text and not is_slang(message.text):
                    is_chat = chatai.find_one({"word": message.reply_to_message.text, "text": message.text})
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.text,
                                "text": message.text,
                                "check": "none",
                            }
                        )
                        REPLY_CACHE["text"].setdefault(message.reply_to_message.text, []).append((message.text, "none"))
    finally:
        chatdb.close()
        vickdb.close()

@VenomX.on_message(
    filters.sticker & filters.group & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker(client: Client, message: Message):
    """Handle sticker-based chatbot responses and learning."""
    chatdb = MongoClient(MONGO_URL)
    vickdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})

        if not is_vick:
            if not message.reply_to_message:
                # Respond with sticker replies from cache if /schatbot is enabled
                if message.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["sticker"][message.sticker.file_unique_id] if t == "sticker"]
                    if replies:
                        reply, check_type = random.choice(replies)
                        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                        await message.reply_sticker(reply)
            elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == client.me.id:
                # Respond with sticker replies from cache if /schatbot is enabled
                if message.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["sticker"][message.sticker.file_unique_id] if t == "sticker"]
                    if replies:
                        reply, check_type = random.choice(replies)
                        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                        await message.reply_sticker(reply)
            elif message.reply_to_message and message.reply_to_message.sticker:
                # Learn new reply (text or sticker)
                if message.text and not is_slang(message.text):
                    is_chat = chatai.find_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.text})
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.sticker.file_unique_id,
                                "text": message.text,
                                "check": "text",
                            }
                        )
                        REPLY_CACHE["sticker"].setdefault(message.reply_to_message.sticker.file_unique_id, []).append((message.text, "text"))
                elif message.sticker:
                    # Sticker-to-sticker learning (no slang filter)
                    is_chat = chatai.find_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.sticker.file_id})
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.sticker.file_unique_id,
                                "text": message.sticker.file_id,
                                "check": "sticker",
                            }
                        )
                        REPLY_CACHE["sticker"].setdefault(message.reply_to_message.sticker.file_unique_id, []).append((message.sticker.file_id, "sticker"))
    finally:
        chatdb.close()
        vickdb.close()

@VenomX.on_message(
    filters.text & ~filters.group & ~filters.bot & ~filters.command(["!", "/", "?", "@", "#"]), group=4
)
async def chatbot_text_pvt(client: Client, message: Message):
    """Handle text-based chatbot responses in private chats."""
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        if not message.reply_to_message or (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == client.me.id):
            # Respond with text replies from cache
            if message.text in REPLY_CACHE["text"]:
                replies = [(r, t) for r, t in REPLY_CACHE["text"][message.text] if t in ["text", "none"]]
                if replies:
                    reply, check_type = random.choice(replies)
                    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                    await message.reply_text(reply)
    finally:
        chatdb.close()

@VenomX.on_message(
    filters.sticker & ~filters.group & ~filters.bot, group=4
)
async def chatbot_sticker_pvt(client: Client, message: Message):
    """Handle sticker-based chatbot responses in private chats."""
    chatdb = MongoClient(MONGO_URL)
    try:
        chatai = chatdb["Word"]["WordDb"]
        if not message.reply_to_message or (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == client.me.id):
            # Respond with sticker replies from cache
            if message.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                replies = [(r, t) for r, t in REPLY_CACHE["sticker"][message.sticker.file_unique_id] if t == "sticker"]
                if replies:
                    reply, check_type = random.choice(replies)
                    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                    await message.reply_sticker(reply)
    finally:
        chatdb.close()
