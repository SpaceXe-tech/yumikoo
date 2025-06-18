import random
import logging
from Abg.chat_status import adminsOnly
from pymongo import MongoClient
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from config import MONGO_URL, OWNER_ID, SUDO_IDS
from Venom import VenomX
from Venom.modules.helpers import CHATBOT_ON, is_admins

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Authorized users for restricted commands
AUTHORIZED_USERS = set([OWNER_ID] + SUDO_IDS)

@VenomX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_(_, m: Message):
    try:
        await m.reply_text(
            f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ʏᴜᴋɪᴛᴀ💐 ᴄʜᴀᴛ-ʙᴏᴛ.**",
            reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
        )
    except Exception as e:
        logger.error(f"Error in chaton_: {e}")
        await m.reply_text("Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ᴀᴄᴛɪᴠᴀᴛɪɴɢ ᴄʜᴀᴛʙᴏᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs.")
    return

@VenomX.on_cmd("rms", group_only=True)
async def remove_sticker_replies(_: Client, m: Message):
    chatdb = None
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏʀ sᴜᴅᴏᴇʀs ᴄᴏᴜʟᴅ ᴜsᴇ /rms ᴄᴍᴅ.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": "sticker"}).deleted_count
        await m.reply_text(f"Rᴇᴍᴏᴠᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ sᴛɪᴄᴋᴇʀ ʀᴇᴘʟɪᴇs ғʀᴏᴍ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ.")
    except Exception as e:
        logger.error(f"Error in remove_sticker_replies: {e}")
        await m.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴍᴏᴠɪɴɢ sᴀᴠᴇᴅ sᴛɪᴄᴋᴇʀ ʀᴇᴘʟɪᴇs.")
    finally:
        if chatdb:
            chatdb.close()

@VenomX.on_cmd("rmm", group_only=True)
async def remove_message_replies(_: Client, m: Message):
    chatdb = None
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏʀ sᴜᴅᴏᴇʀs ᴄᴏᴜʟᴅ ᴜsᴇ /rmm ᴄᴍᴅ.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": {"$in": ["text", "none"]}}).deleted_count
        await m.reply_text(f"ᴠᴀɴɪsʜᴇᴅ {deleted} ʟᴇᴀʀɴᴇᴅ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇs ғʀᴏᴍ ᴍʏ ᴍᴇᴍᴏʀʏ.")
    except Exception as e:
        logger.error(f"Error in remove_message_replies: {e}")
        await m.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴍᴏᴠɪɴɢ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇs.")
    finally:
        if chatdb:
            chatdb.close()

@VenomX.on_cmd("clear", group_only=True)
async def clear_all_replies(_: Client, m: Message):
    chatdb = None
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏʀ sᴜᴅᴏᴇʀs ᴄᴏᴜʟᴅ ᴜsᴇ /clear ᴄᴍᴅ.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({}).deleted_count
        await m.reply_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ 🍃 ᴠᴀɴɪsʜᴇᴅ ᴀʟʟ {deleted} ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟɪᴇs ғʀᴏᴍ ᴍʏ ᴍᴇᴍᴏʀɪᴇs.")
    except Exception as e:
        logger.error(f"Error in clear_all_replies: {e}")
        await m.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴍᴏᴠɪɴɢ ᴀʟʟ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟɪᴇs.")
    finally:
        if chatdb:
            chatdb.close()

@VenomX.on_cmd("rem", group_only=True)
async def remove_specific_reply(_: Client, m: Message):
    chatdb = None
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏʀ sᴜᴅᴏᴇʀs ᴄᴏᴜʟᴅ ᴜsᴇ /rem ᴄᴍᴅ.")
            return
        if not m.reply_to_message:
            await m.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴍʏ ʟᴇᴀʀɴᴇᴅ ᴄʜᴀᴛ ʀᴇᴘʟɪᴇs.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        if m.reply_to_message.text:
            deleted = chatai.delete_one({"text": m.reply_to_message.text}).deleted_count
        elif m.reply_to_message.sticker:
            deleted = chatai.delete_one({"text": m.reply_to_message.sticker.file_id}).deleted_count
        else:
            await m.reply_text("Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ʀᴇᴍᴏᴠᴀʟ ᴛʏᴘᴇ. ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ.")
            return
        if deleted > 0:
            await m.reply_text("ᴠᴀɴɪsʜᴇᴅ ᴛʜᴇ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟʏ ғʀᴏᴍ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ.")
        else:
            await m.reply_text("ɴᴏ ᴍᴀᴛᴄʜɪɴɢ ʟᴇᴀʀɴᴇᴅ sᴀᴠᴇᴅ ʀᴇᴘʟɪᴇs ғᴏᴜɴᴅ sᴏ ғᴀʀ ɪɴ ᴍʏ ᴍᴇᴍᴏʀʏ.")
    except Exception as e:
        logger.error(f"Error in remove_specific_reply: {e}")
        await m.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴍᴏᴠɪɴɢ ᴛʜᴇ sᴘᴇᴄɪғɪᴄ ʟᴇᴀʀɴᴇᴅ ʀᴇᴘʟɪᴇs.")
    finally:
        if chatdb:
            chatdb.close()

@VenomX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_text(client: Client, message: Message):
    chatdb = None
    vickdb = None
    try:
        if message.text and (
            message.text.startswith("!") or
            message.text.startswith("/") or
            message.text.startswith("?") or
            message.text.startswith("@") or
            message.text.startswith("#")
        ):
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})

        if not is_vick:
            if not message.reply_to_message:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "sticker":
                        await message.reply_sticker(f"{hey}")
                    else:
                        await message.reply_text(f"{hey}")
            elif message.reply_to_message.from_user.id == client.me.id:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "sticker":
                        await message.reply_sticker(f"{hey}")
                    else:
                        await message.reply_text(f"{hey}")
            elif message.reply_to_message.text:
                if message.sticker:
                    is_chat = chatai.find_one(
                        {"word": message.reply_to_message.text, "id": message.sticker.file_unique_id}
                    )
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.text,
                                "text": message.sticker.file_id,
                                "check": "sticker",
                                "id": message.sticker.file_unique_id,
                            }
                        )
                elif message.text:
                    is_chat = chatai.find_one(
                        {"word": message.reply_to_message.text, "text": message.text}
                    )
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.text,
                                "text": message.text,
                                "check": "none",
                            }
                        )
    except Exception as e:
        logger.error(f"Error in chatbot_text: {e}")
    finally:
        if chatdb:
            chatdb.close()
        if vickdb:
            vickdb.close()

@VenomX.on_message(
    (filters.sticker | filters.group | filters.text) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker(client: Client, message: Message):
    chatdb = None
    vickdb = None
    try:
        if message.text and (
            message.text.startswith("!") or
            message.text.startswith("/") or
            message.text.startswith("?") or
            message.text.startswith("@") or
            message.text.startswith("#")
        ):
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})

        if not is_vick:
            if not message.reply_to_message:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.sticker.file_unique_id})
                k = chatai.find_one({"word": message.sticker.file_unique_id})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "text":
                        await message.reply_text(f"{hey}")
                    else:
                        await message.reply_sticker(f"{hey}")
            elif message.reply_to_message.from_user.id == client.me.id:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.sticker.file_unique_id})
                k = chatai.find_one({"word": message.sticker.file_unique_id})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "text":
                        await message.reply_text(f"{hey}")
                    else:
                        await message.reply_sticker(f"{hey}")
            elif message.reply_to_message.sticker:
                if message.text:
                    is_chat = chatai.find_one(
                        {"word": message.reply_to_message.sticker.file_unique_id, "text": message.text}
                    )
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.sticker.file_unique_id,
                                "text": message.text,
                                "check": "text",
                            }
                        )
                elif message.sticker:
                    is_chat = chatai.find_one(
                        {"word": message.reply_to_message.sticker.file_unique_id, "text": message.sticker.file_id}
                    )
                    if not is_chat:
                        chatai.insert_one(
                            {
                                "word": message.reply_to_message.sticker.file_unique_id,
                                "text": message.sticker.file_id,
                                "check": "none",
                            }
                        )
    except Exception as e:
        logger.error(f"Error in chatbot_sticker: {e}")
    finally:
        if chatdb:
            chatdb.close()
        if vickdb:
            vickdb.close()

@VenomX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_pvt(client: Client, message: Message):
    chatdb = None
    try:
        if message.text and (
            message.text.startswith("!") or
            message.text.startswith("/") or
            message.text.startswith("?") or
            message.text.startswith("@") or
            message.text.startswith("#")
        ):
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        if not message.reply_to_message:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.text})
            for x in is_chat:
                K.append(x["text"])
            if K:
                hey = random.choice(K)
                is_text = chatai.find_one({"text": None})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                else:
                    await message.reply_text(f"{hey}")
        elif message.reply_to_message.from_user.id == client.me.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.text})
            for x in is_chat:
                K.append(x["text"])
            if K:
                hey = random.choice(K)
                is_text = chatai.find_one({"text": None})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                else:
                    await message.reply_text(f"{hey}")
    except Exception as e:
        logger.error(f"Error in chatbot_pvt: {e}")
    finally:
        if chatdb:
            chatdb.close()

@VenomX.on_message(
    (filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker_pvt(client: Client, message: Message):
    chatdb = None
    try:
        if message.text and (
            message.text.startswith("!") or
            message.text.startswith("/") or
            message.text.startswith("?") or
            message.text.startswith("@") or
            message.text.startswith("#")
        ):
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        if not message.reply_to_message:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.sticker.file_unique_id})
            for x in is_chat:
                K.append(x["text"])
            if K:
                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "text":
                    await message.reply_text(f"{hey}")
                else:
                    await message.reply_sticker(f"{hey}")
        elif message.reply_to_message.from_user.id == client.me.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.sticker.file_unique_id})
            for x in is_chat:
                K.append(x["text"])
            if K:
                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "text":
                    await message.reply_text(f"{hey}")
                else:
                    await message.reply_sticker(f"{hey}")
    except Exception as e:
        logger.error(f"Error in chatbot_sticker_pvt: {e}")
    finally:
        if chatdb:
            chatdb.close()
