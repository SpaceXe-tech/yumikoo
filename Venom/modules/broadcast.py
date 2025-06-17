from pyrogram import Client, filters
from pyrogram.types import Message
from Venom import VenomX, config
from Venom.database.users import get_served_users
from Venom.database.chats import get_served_chats
import asyncio

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_ID = config.SUDO_ID
AUTHORIZED_USERS = [OWNER_ID] + (SUDO_ID if isinstance(SUDO_ID, list) else [SUDO_ID])

async def broadcast_to_users(app: Client, message: Message, text: str = None, media: bool = False, forward: bool = False):
    """
    Broadcast a message to all served users.
    
    Args:
        app (Client): Pyrogram client instance
        message (Message): The message to broadcast (for reply or media)
        text (str, optional): Text to send if no message is provided
        media (bool): Whether to send media from the message
        forward (bool): Whether to forward the message (preserves emojis)
    """
    success_count = 0
    failed_count = 0
    users = await get_served_users()
    
    for user in users:
        user_id = user["user_id"]
        try:
            if forward and message.reply_to_message:
                await message.reply_to_message.forward(user_id)
            elif media and message.media:
                if message.photo:
                    await app.send_photo(user_id, message.photo.file_id, caption=message.caption or text)
                elif message.video:
                    await app.send_video(user_id, message.video.file_id, caption=message.caption or text)
                elif message.document:
                    await app.send_document(user_id, message.document.file_id, caption=message.caption or text)
                else:
                    await app.send_message(user_id, text or message.text)
            else:
                await app.send_message(user_id, text or message.text)
            success_count += 1
            await asyncio.sleep(0.1)  # Avoid flood limits
        except:
            failed_count += 1
            continue
    
    return success_count, failed_count

async def broadcast_to_chats(app: Client, message: Message, text: str = None, media: bool = False, forward: bool = False):
    """
    Broadcast a message to all served chats.
    
    Args:
        app (Client): Pyrogram client instance
        message (Message): The message to broadcast (for reply or media)
        text (str, optional): Text to send if no message is provided
        media (bool): Whether to send media from the message
        forward (bool): Whether to forward the message (preserves emojis)
    """
    success_count = 0
    failed_count = 0
    chats = await get_served_chats()
    
    for chat in chats:
        chat_id = chat["chat_id"]
        try:
            if forward and message.reply_to_message:
                await message.reply_to_message.forward(chat_id)
            elif media and message.media:
                if message.photo:
                    await app.send_photo(chat_id, message.photo.file_id, caption=message.caption or text)
                elif message.video:
                    await app.send_video(chat_id, message.video.file_id, caption=message.caption or text)
                elif message.document:
                    await app.send_document(chat_id, message.document.file_id, caption=message.caption or text)
                else:
                    await app.send_message(chat_id, text or message.text)
            else:
                await app.send_message(chat_id, text or message.text)
            success_count += 1
            await asyncio.sleep(0.1)  # Avoid flood limits
        except:
            failed_count += 1
            continue
    
    return success_count, failed_count

@VenomX.on_message(filters.command("broadcast") & filters.user(AUTHORIZED_USERS))
async def broadcast_command(_: Client, message: Message):
    """
    Command handler for /broadcast command.
    Usage: 
        /broadcast [text] - Broadcast text to all users/chats
        /broadcast users [text] - Broadcast text to users
        /broadcast chats [text] - Broadcast text to chats
        /broadcast -forward - Forward replied message (preserves emojis)
        /broadcast users -forward - Forward to users only
        /broadcast chats -forward - Forward to chats only
    """
    args = message.text.split(maxsplit=2)
    forward = "-forward" in args
    target = "all"
    text = None

    if forward:
        if not message.reply_to_message:
            await message.reply("Please reply to a message to forward.")
            return
        args.remove("-forward")
        text = None
    else:
        text = args[2] if len(args) > 2 else None
        if not text and not message.reply_to_message:
            await message.reply("Please provide a message to broadcast or reply to a message.")
            return

    if len(args) > 1 and args[1] in ["users", "chats"]:
        target = args[1]

    media = bool(message.reply_to_message and message.reply_to_message.media and not forward)
    await message.reply("Starting broadcast...")

    total_success = 0
    total_failed = 0

    if target in ["users", "all"]:
        success, failed = await broadcast_to_users(VenomX, message.reply_to_message or message, text, media, forward)
        total_success += success
        total_failed += failed
        await message.reply(f"User broadcast completed: {success} successful, {failed} failed.")

    if target in ["chats", "all"]:
        success, failed = await broadcast_to_chats(VenomX, message.reply_to_message or message, text, media, forward)
        total_success += success
        total_failed += failed
        await message.reply(f"Chat broadcast completed: {success} successful, {failed} failed.")

    await message.reply(f"Broadcast summary: {total_success} successful, {total_failed} failed.")
