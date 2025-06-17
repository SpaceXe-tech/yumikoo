from pyrogram import filters, Client
from pyrogram.types import Message
from Venom import VenomX, config
from Venom.database.chats import get_served_chats
from Venom.database.users import get_served_users

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_IDS = config.SUDO_IDS
AUTHORIZED_USERS = [OWNER_ID] + SUDO_IDS

@VenomX.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /stats.")
        return
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""ᴛᴏᴛᴀʟ sᴛᴀᴛs ᴏғ {(await cli.get_me()).mention} :

➻ **ᴄʜᴀᴛs :** {chats}
➻ **ᴜsᴇʀs :** {users}"""
    )
