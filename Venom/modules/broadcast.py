from pyrogram import filters, Client
from pyrogram.types import Message
from Venom import VenomX, config
from Venom.database.users import get_served_users
from Venom.database.chats import get_served_chats
import asyncio

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

async def broadcast_message(app: Client, message: Message, targets: list, forward: bool = False, exclude_bots: bool = False, progress_msg: Message = None):
    """
    Broadcast or forward a message to specified targets with realtime updates.
    
    Args:
        app (Client): Pyrogram client instance
        message (Message): The message to broadcast or forward
        targets (list): List of "users" and/or "groups"
        forward (bool): Whether to forward the message (preserves emojis, inline buttons)
        exclude_bots (bool): Exclude bot chats
        progress_msg (Message): Message to edit for progress updates
    """
    success_count = 0
    failed_count = 0
    total_processed = 0
    update_interval = 10  # Update every 10 messages

    # Handle users
    if "users" in targets:
        users = await get_served_users()
        for user in users:
            user_id = user["user_id"]
            try:
                if forward:
                    await message.forward(user_id)
                else:
                    await message.copy(user_id)
                success_count += 1
            except:
                failed_count += 1
            total_processed += 1
            if total_processed % update_interval == 0 and progress_msg:
                await progress_msg.edit_text(f"Progress: {success_count} successful, {failed_count} failed...")
            await asyncio.sleep(0.05)  # 20 messages/second

    # Handle groups
    if "groups" in targets:
        chats = await get_served_chats()
        for chat in chats:
            chat_id = chat["chat_id"]
            try:
                if exclude_bots:
                    chat_info = await app.get_chat(chat_id)
                    if chat_info.type == "bot":
                        continue
                if forward:
                    await message.forward(chat_id)
                else:
                    await message.copy(chat_id)
                success_count += 1
            except:
                failed_count += 1
            total_processed += 1
            if total_processed % update_interval == 0 and progress_msg:
                await progress_msg.edit_text(f"Progress: {success_count} successful, {failed_count} failed...")
            await asyncio.sleep(0.05)  # 20 messages/second

    return success_count, failed_count

@VenomX.on_message(filters.command("broadcast"))
async def broadcast_command(_: Client, message: Message):
    """
    Command handler for /broadcast command.
    Usage:
        /broadcast - Reply to a message to broadcast it (copy) to all users and groups
        /broadcast -all - Same as above
        /broadcast -f - Forward replied message to all users and groups
        /broadcast -f -users -groups -nobot - Forward to specified targets, exclude bots
        /broadcast -users -groups -nobot - Copy to specified targets, exclude bots
    """
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /broadcast.")
        return

    if not message.reply_to_message:
        await message.reply("Please reply to a message to broadcast.")
        return

    args = message.text.split()
    forward = "-f" in args
    exclude_bots = "-nobot" in args
    targets = ["users", "groups"] if "-all" in args or len(args) == 1 else []
    
    if "-users" in args:
        targets.append("users")
    if "-groups" in args:
        targets.append("groups")
    if not targets:
        targets = ["users", "groups"]  # Default to all if no valid targets

    progress_msg = await message.reply("Starting broadcast...")

    success, failed = await broadcast_message(VenomX, message.reply_to_message, targets, forward, exclude_bots, progress_msg)
    await progress_msg.edit_text(f"Broadcast completed: {success} successful, {failed} failed.")
