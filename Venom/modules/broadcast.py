import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError
from Venom import VenomX, config
from Venom.database.users import get_served_users
from Venom.database.chats import get_served_chats

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

async def broadcast_message(app: Client, message: Message, targets: list, forward: bool = False, exclude_bots: bool = False, progress_msg: Message = None):
    """
    Broadcast or forward a message to specified targets sequentially with detailed progress updates.
    
    Args:
        app (Client): Pyrogram client instance
        message (Message): The message to broadcast or forward
        targets (list): List of "users" and/or "groups"
        forward (bool): Whether to forward the message
        exclude_bots (bool): Exclude bot chats
        progress_msg (Message): Message to edit for progress updates
    """
    success_groups = 0
    failed_groups = 0
    success_users = 0
    failed_users = 0
    update_interval = 10  # Update every 10 messages

    # Function to update progress message
    async def update_progress():
        if progress_msg:
            await progress_msg.edit_text(
                f"Broadcast Progress:\n"
                f"Groups: {success_groups} successful, {failed_groups} failed\n"
                f"Users: {success_users} successful, {failed_users} failed"
            )

    # Handle groups first
    if "groups" in targets:
        chats = await get_served_chats()
        for chat in chats:
            chat_id = chat["chat_id"]
            try:
                # Skip bot chats if exclude_bots is True
                if exclude_bots:
                    chat_info = await app.get_chat(chat_id)
                    if chat_info.type == "bot":
                        continue
                # Attempt to send message
                if forward:
                    await message.forward(chat_id)
                else:
                    await message.copy(chat_id)
                success_groups += 1
            except RPCError:  # Skip invalid or inaccessible chats
                failed_groups += 1
                continue
            if (success_groups + failed_groups) % update_interval == 0:
                await update_progress()
            await asyncio.sleep(0.05)  # Rate limiting: 20 messages/second
        await update_progress()  # Final update for groups

    # Handle users after groups
    if "users" in targets:
        users = await get_served_users()
        for user in users:
            user_id = user["user_id"]
            try:
                # Attempt to send message
                if forward:
                    await message.forward(user_id)
                else:
                    await message.copy(user_id)
                success_users += 1
            except RPCError:  # Skip invalid or inaccessible users
                failed_users += 1
                continue
            if (success_users + failed_users) % update_interval == 0:
                await update_progress()
            await asyncio.sleep(0.05)  # Rate limiting: 20 messages/second
        await update_progress()  # Final update for users

    return success_groups, failed_groups, success_users, failed_users

@VenomX.on_message(filters.command("broadcast"))
async def broadcast_command(_: Client, message: Message):
    """
    Command handler for /broadcast command.
    Usage:
        /broadcast or /broadcast -all or /broadcast -f -all - Broadcast (copy/forward) to all users and groups
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

    progress_msg = await message.reply("Starting broadcast...\nGroups: 0 successful, 0 failed\nUsers: 0 successful, 0 failed")
    
    success_g, failed_g, success_u, failed_u = await broadcast_message(
        VenomX, message.reply_to_message, targets, forward, exclude_bots, progress_msg
    )
    
    await progress_msg.edit_text(
        f"Broadcast completed:\n"
        f"Groups: {success_g} successful, {failed_g} failed\n"
        f"Users: {success_u} successful, {failed_u} failed"
                    )
