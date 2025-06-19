import asyncio
import time
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait
from Venom import VenomX, config
from Venom.database.users import get_served_users
from Venom.database.chats import get_served_chats
import logging

# Configure logging for critical errors only
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

async def broadcast_message(app: Client, message: Message, targets: list, forward: bool = False, exclude_bots: bool = False, progress_msg: Message = None):
    """
    Broadcast or forward a message to specified targets with optimized batch processing and real-time progress updates.
    
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
    batch_size = 30  # Telegram's limit: 30 messages/second for bots
    update_interval = 20  # Update progress every 20 targets
    min_delay = 0.01  # Minimal delay for max throughput

    # Function to update progress message
    async def update_progress(total_processed: int, is_groups: bool):
        if progress_msg:
            try:
                await progress_msg.edit_text(
                    f"Broadcast Progress:\n"
                    f"Groups: {success_groups} successful, {failed_groups} failed\n"
                    f"Users: {success_users} successful, {failed_users} failed\n"
                    f"{'Groups' if is_groups else 'Users'} processed: {total_processed}"
                )
            except RPCError as e:
                logger.critical(f"Critical: Failed to update progress: {e}")

    # Process targets in batches
    async def process_batch(target_ids, is_groups: bool):
        nonlocal success_groups, failed_groups, success_users, failed_users
        total_processed = 0

        for i in range(0, len(target_ids), batch_size):
            batch = target_ids[i:i + batch_size]
            tasks = []
            for target_id in batch:
                try:
                    # Skip bot chats if exclude_bots is True (for groups only)
                    if is_groups and exclude_bots:
                        chat_info = await app.get_chat(target_id)
                        if chat_info.type == "bot":
                            failed_groups += 1
                            total_processed += 1
                            continue
                    # Create task for sending message
                    if forward:
                        tasks.append((target_id, message.forward(target_id)))
                    else:
                        tasks.append((target_id, message.copy(target_id)))
                except RPCError:
                    if is_groups:
                        failed_groups += 1
                    else:
                        failed_users += 1
                    total_processed += 1
                    continue

            # Execute batch with adaptive rate limiting
            start_time = time.time()
            try:
                results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
                for (target_id, _), result in zip(tasks, results):
                    if isinstance(result, RPCError):
                        if is_groups:
                            failed_groups += 1
                        else:
                            failed_users += 1
                    else:
                        if is_groups:
                            success_groups += 1
                        else:
                            success_users += 1
                    total_processed += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
                for (target_id, _), result in zip(tasks, results):
                    if isinstance(result, RPCError):
                        if is_groups:
                            failed_groups += 1
                        else:
                            failed_users += 1
                    else:
                        if is_groups:
                            success_groups += 1
                        else:
                            success_users += 1
                    total_processed += 1

            # Adaptive delay to stay under rate limits
            elapsed = time.time() - start_time
            expected_time = len(tasks) / 30  # 30 messages per second
            if elapsed < expected_time:
                await asyncio.sleep(min(min_delay * len(tasks), expected_time - elapsed))

            # Update progress frequently
            if total_processed % update_interval == 0:
                await update_progress(total_processed, is_groups)

        # Final progress update for this target type
        await update_progress(total_processed, is_groups)

    # Pre-fetch all IDs to minimize database overhead
    chat_ids = [chat["chat_id"] for chat in await get_served_chats()] if "groups" in targets else []
    user_ids = [user["user_id"] for user in await get_served_users()] if "users" in targets else []

    # Handle groups first
    if chat_ids:
        await process_batch(chat_ids, is_groups=True)

    # Handle users after groups
    if user_ids:
        await process_batch(user_ids, is_groups=False)

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
    
    start_time = time.time()
    success_g, failed_g, success_u, failed_u = await broadcast_message(
        VenomX, message.reply_to_message, targets, forward, exclude_bots, progress_msg
    )
    
    elapsed_time = time.time() - start_time
    await progress_msg.edit_text(
        f"Broadcast completed in {elapsed_time:.2f} seconds:\n"
        f"Groups: {success_g} successful, {failed_g} failed\n"
        f"Users: {success_u} successful, {failed_u} failed"
                        )
