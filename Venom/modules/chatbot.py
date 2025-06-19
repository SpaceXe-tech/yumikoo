import random
import re
import os
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from Abg.chat_status import adminsOnly
from config import MONGO_URL, OWNER_ID, SUDO_IDS
from Venom import VenomX
from Venom.modules.helpers import CHATBOT_ON

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
    with MongoClient(MONGO_URL) as chatdb:
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

# Load cache on startup
load_cache()

# Custom filter to exclude messages starting with specific prefixes
def not_command():
    async def func(_, __, message):
        return not message.text or not re.match(r'^[!/?@#]', message.text)
    return filters.create(func)

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
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": "sticker"}).deleted_count
        REPLY_CACHE["sticker"].clear()
        await m.reply_text(f"Rᴇᴍᴏᴠᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ sᴛɪᴄᴋᴇʀ ʀᴇᴘʄɪᴇs.")

@VenomX.on_cmd("rmm", group_only=True)
async def remove_message_replies(_: Client, m: Message):
    """Remove all learned text message replies."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": {"$in": ["text", "none"]}}).deleted_count
        REPLY_CACHE["text"].clear()
        await m.reply_text(f"ᴠᴀɴɪsʜᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ ᴍᴇssᴀɢᴇ ʀᴇᴘʄɪᴇs.")

@VenomX.on_cmd("clear", group_only=True)
async def clear_all_replies(_: Client, m: Message):
    """Remove all learned replies."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({}).deleted_count
        REPLY_CACHE["text"].clear()
        REPLY_CACHE["sticker"].clear()
        await m.reply_text(f"sᴜᴄᴄᴇssғᴜʄʄʏ 🍃 ᴠᴀɴɪsʜᴇᴅ ᴀʄʄ {deleted} ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʄɪᴇs.")

@VenomX.on_cmd("rem", group_only=True)
async def remove_specific_reply(_: Client, m: Message):
    """Remove a specific learned reply."""
    if m.from_user.id not in AUTHORIZED_USERS:
        await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    if not m.reply_to_message:
        await m.reply_text("ᴘʄᴇᴀsᴇ ʀᴇᴘʄʏ ᴛᴏ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ.")
        return
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        deleted = 0
        if m.reply_to_message.text:
            deleted = chatai.delete_many({"text": m.reply_to_message.text, "check": {"$in": ["text", "none"]}}).deleted_count
            for word, replies in list(REPLY_CACHE["text"].items()):
                REPLY_CACHE["text"][word] = [(r, t) for r, t in replies if r != m.reply_to_message.text]
                if not REPLY_CACHE["text"][word]:
                    del REPLY_CACHE["text"][word]
        elif m.reply_to_message.sticker:
            deleted = chatai.delete_many({"text": m.reply_to_message.sticker.file_id, "check": "sticker"}).deleted_count
            for word, replies in list(REPLY_CACHE["sticker"].items()):
                REPLY_CACHE["sticker"][word] = [(r, t) for r, t in replies if r != m.reply_to_message.sticker.file_id]
                if not REPLY_CACHE["sticker"][word]:
                    del REPLY_CACHE["sticker"][word]
        else:
            await m.reply_text("Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ʀᴇᴍᴏᴠᴀʄ ᴛʏᴘᴇ. ʀᴇᴘʄʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ.")
            return
        if deleted > 0:
            await m.reply_text("ᴠᴀɴɪsʜᴇᴠ ᴛʜᴇ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʄʏ.")
        else:
            await m.reply_text("ɴᴏ ᴍᴀᴛᴄʜɪɴɢ ʄᴇᴀʀɴᴇᴅ ʀᴇᴘʄɪᴇs ғᴏᴜɴᴅ.")

@VenomX.on_message(filters.text & filters.group & ~filters.private & ~filters.bot & not_command(), group=4)
async def chatbot_text(client: Client, m: Message):
    """Handle text-based chatbot responses and learning in group chats."""
    with MongoClient(MONGO_URL) as db:
        chatai = db["Word"]["WordDb"]
        vick = db["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": m.chat.id})

        if not is_vick:
            if not m.reply_to_message:
                if m.text in REPLY_CACHE["text"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["text"][m.text] if t in ["text", "none"]]
                    if replies:
                        reply, _ = random.choice(replies)
                        await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                        await m.reply_text(reply)
            elif m.reply_to_message.from_user and m.reply_to_message.from_user.id == client.me.id:
                if m.text in REPLY_CACHE["text"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["text"][m.text] if t in ["text", "none"]]
                    if replies:
                        reply, _ = random.choice(replies)
                        await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                        await m.reply_text(reply)
            elif m.reply_to_message.text:
                if m.sticker:
                    if not chatai.find_one({"word": m.reply_to_message.text, "id": m.sticker.file_unique_id}):
                        chatai.insert_one({
                            "word": m.reply_to_message.text,
                            "text": m.sticker.file_id,
                            "check": "sticker",
                            "id": m.sticker.file_unique_id
                        })
                        REPLY_CACHE["text"].setdefault(m.reply_to_message.text, []).append((m.sticker.file_id, "sticker"))
                elif m.text and not is_slang(m.text):
                    if not chatai.find_one({"word": m.reply_to_message.text, "text": m.text}):
                        chatai.insert_one({
                            "word": m.reply_to_message.text,
                            "text": m.text,
                            "check": "none"
                        })
                        REPLY_CACHE["text"].setdefault(m.reply_to_message.text, []).append((m.text, "none"))

@VenomX.on_message(filters.sticker & filters.group & ~filters.private & ~filters.bot, group=4)
async def chatbot_sticker(client: Client, m: Message):
    """Handle sticker-based chatbot responses and learning in group chats."""
    with MongoClient(MONGO_URL) as db:
        chatai = db["Word"]["WordDb"]
        vick = db["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": m.chat.id})

        if not is_vick:
            if not m.reply_to_message:
                if m.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["sticker"][m.sticker.file_unique_id] if t == "sticker"]
                    if replies:
                        reply, _ = random.choice(replies)
                        await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                        await m.reply_sticker(reply)
            elif m.reply_to_message.from_user and m.reply_to_message.from_user.id == client.me.id:
                if m.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                    replies = [(r, t) for r, t in REPLY_CACHE["sticker"][m.sticker.file_unique_id] if t == "sticker"]
                    if replies:
                        reply, _ = random.choice(replies)
                        await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                        await m.reply_sticker(reply)
            elif m.reply_to_message.sticker:
                if m.text and not is_slang(m.text):
                    if not chatai.find_one({"word": m.reply_to_message.sticker.file_unique_id, "text": m.text}):
                        chatai.insert_one({
                            "word": m.reply_to_message.sticker.file_unique_id,
                            "text": m.text,
                            "check": "text"
                        })
                        REPLY_CACHE["sticker"].setdefault(m.reply_to_message.sticker.file_unique_id, []).append((m.text, "text"))
                elif m.sticker:
                    if not chatai.find_one({"word": m.reply_to_message.sticker.file_unique_id, "text": m.sticker.file_id}):
                        chatai.insert_one({
                            "word": m.reply_to_message.sticker.file_unique_id,
                            "text": m.sticker.file_id,
                            "check": "sticker"
                        })
                        REPLY_CACHE["sticker"].setdefault(m.reply_to_message.sticker.file_unique_id, []).append((m.sticker.file_id, "sticker"))

@VenomX.on_message(filters.text & ~filters.group & ~filters.bot & not_command(), group=4)
async def chatbot_text_pvt(client: Client, m: Message):
    """Handle text-based chatbot responses in private chats."""
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        if not m.reply_to_message or (m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.id == client.me.id):
            if m.text in REPLY_CACHE["text"]:
                replies = [(r, t) for r, t in REPLY_CACHE["text"][m.text] if t in ["text", "none"]]
                if replies:
                    reply, _ = random.choice(replies)
                    await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                    await m.reply_text(reply)

@VenomX.on_message(filters.sticker & ~filters.group & ~filters.bot, group=4)
async def chatbot_sticker_pvt(client: Client, m: Message):
    """Handle sticker-based chatbot responses in private chats."""
    with MongoClient(MONGO_URL) as chatdb:
        chatai = chatdb["Word"]["WordDb"]
        if not m.reply_to_message or (m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.id == client.me.id):
            if m.sticker.file_unique_id in REPLY_CACHE["sticker"]:
                replies = [(r, t) for r, t in REPLY_CACHE["sticker"][m.sticker.file_unique_id] if t == "sticker"]
                if replies:
                    reply, _ = random.choice(replies)
                    await client.send_chat_action(m.chat.id, ChatAction.TYPING)
                    await m.reply_sticker(reply)
