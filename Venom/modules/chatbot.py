
import random
import random
from Abg.chat_status import adminsOnly
from pymongo import MongoClient
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from config import MONGO_URL, OWNER_ID, SUDO_ID
from Venom import VenomX
from Venom.modules.helpers import CHATBOT_ON, is_admins

# Authorized users for restricted commands
AUTHORIZED_USERS = set([OWNER_ID] + SUDO_ID)

@VenomX.on_cmd("chatbot", group_only=True)
@adminsOnly("can_delete_messages")
async def chaton_(_, m: Message):
    try:
        await m.reply_text(
            f"ᴄʜᴀᴛ: {m.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
            reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
        )
    except:
        await m.reply_text("An error occurred. Please try again.")
    return

@VenomX.on_cmd("rms", group_only=True)
async def remove_sticker_replies(_: Client, m: Message):
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /rms.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": "sticker"}).deleted_count
        await m.reply_text(f"Removed {deleted} learned sticker replies from the database.")
    except:
        await m.reply_text("An error occurred while removing sticker replies.")
    finally:
        chatdb.close()

@VenomX.on_cmd("rmm", group_only=True)
async def remove_message_replies(_: Client, m: Message):
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /rmm.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({"check": {"$in": ["text", "none"]}}).deleted_count
        await m.reply_text(f"Removed {deleted} learned message replies from the database.")
    except:
        await m.reply_text("An error occurred while removing message replies.")
    finally:
        chatdb.close()

@VenomX.on_cmd("clear", group_only=True)
async def clear_all_replies(_: Client, m: Message):
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /clear.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        deleted = chatai.delete_many({}).deleted_count
        await m.reply_text(f"Cleared all {deleted} learned replies from the database.")
    except:
        await m.reply_text("An error occurred while clearing all replies.")
    finally:
        chatdb.close()

@VenomX.on_cmd("rem", group_only=True)
async def remove_specific_reply(_: Client, m: Message):
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /rem.")
            return
        if not m.reply_to_message:
            await m.reply_text("Please reply to the message or sticker you want to remove from learned replies.")
            return
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        if m.reply_to_message.text:
            deleted = chatai.delete_one({"text": m.reply_to_message.text}).deleted_count
        elif m.reply_to_message.sticker:
            deleted = chatai.delete_one({"text": m.reply_to_message.sticker.file_id}).deleted_count
        else:
            await m.reply_text("Unsupported reply type. Reply to a text message or sticker.")
            return
        if deleted > 0:
            await m.reply_text("Removed the learned reply from the database.")
        else:
            await m.reply_text("No matching learned reply found in the database.")
    except:
        await m.reply_text("An error occurred while removing the specific reply.")
    finally:
        chatdb.close()

@VenomX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_text(client: Client, message: Message):
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
    except:
        pass
    finally:
        chatdb.close()
        vickdb.close()

@VenomX.on_message(
    (filters.sticker | filters.group | filters.text) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker(client: Client, message: Message):
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
    except:
        pass
    finally:
        chatdb.close()
        vickdb.close()

@VenomX.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_pvt(client: Client, message: Message):
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
            for x in is_chat:
                K.append(x["text"])
            if K:
                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                else:
                    await message.reply_text(f"{hey}")
    except:
        pass
    finally:
        chatdb.close()

@VenomX.on_message(
    (filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_sticker_pvt(client: Client, message: Message):
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
    except:
        pass
    finally:
        chatdb.close()
