import asyncio
import time
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait
from Venom import VenomX, config
from Venom.database.users import get_served_users
from Venom.database.chats import get_served_chats

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

async def broadcast_message(app: Client, message: Message, targets: list, forward: bool = False, exclude_bots: bool = False, progress_msg: Message = None):
    """
    Broadcast or forward a message to specified targets sequentially with batch processing and adaptive rate limiting.
    
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
    batch_size = 30  # Telegram allows 30 messages per second for bots
    update_interval = 50  # Update progress every 50 processed targets
    min_delay = 0.033  # Minimum delay for 30 messages/second

    # Function to update progress message
    async def update_progress():
        if progress_msg:
            await progress_msg.edit_text(
                f"Broadcast Progress:\n"
                f"Groups: {success_groups} successful, {failed_groups} failed\n"
                f"Users: {success_users} successful, {failed_users} failed"
            )

    # Process targets in batches
    async def process_batch(target_ids, is_groups: bool):
        nonlocal success_groups, failed_groups, success_users, failed_users
        tasks = []
        for target_id in target_ids:
            try:
                # Skip bot chats if exclude_bots is True (for groups only)
                if is_groups and exclude_bots:
                    chat_info = await app.get_chat(target_id)
                    if chat_info.type == "bot":
                        if is_groups:
                            failed_groups += 1
                        continue
                
                # Create task for sending message
                if forward:
                    tasks.append(message.forward(target_id))
                else:
                    tasks.append(message.copy(target_id))
            except RPCError:
                if is_groups:
                    failed_groups += 1
                else:
                    failed_users += 1
                continue

        # Execute batch with adaptive rate limiting
        start_time = time.time()
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            try:
                await asyncio.gather(*batch)
                if is_groups:
                    success_groups += len(batch)
                else:
                    success_users += len(batch)
            except FloodWait as e:
                await asyncio.sleep(e.value)  # Wait for flood limit
                await asyncio.gather(*batch)
                if is_groups:
                    success_groups += len(batch)
                else:
                    success_users += len(batch)
            except RPCError:
                if is_groups:
                    failed_groups += len(batch)
                else:
                    failed_users += len(batch)
                continue
            
            # Adaptive delay to stay under rate limits
            elapsed = time.time() - start_time
            expected_time = (i + len(batch)) / 30  # 30 messages per second
            if elapsed < expected_time:
                await asyncio.sleep(min_delay * len(batch))

            # Update progress
            total_processed = (success_groups + failed_groups) if is_groups else (success_users + failed_users)
            if total_processed % update_interval == 0:
                await update_progress()

    # Handle groups first
    if "groups" in targets:
        chats = await get_served_chats()
        chat_ids = [chat["chat_id"] for chat in chats]
        await process_batch(chat_ids, is_groups=True)
        await update_progress()  # Final update for groups

    # Handle users after groups
    if "users" in targets:
        users = await get_served_users()
        user_ids = [user["user_id"] for user in users]
        await process_batch(user_ids, is_groups=False)
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
