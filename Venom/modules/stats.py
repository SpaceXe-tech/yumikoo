from pyrogram import filters, Client
from pyrogram.types import Message
from Venom import VenomX, config
from Venom.database.chats import get_served_chats
from Venom.database.users import get_served_users

# Authorized users
OWNER_ID = config.OWNER_ID
SUDO_ID = config.SUDO_ID
AUTHORIZED_USERS = [OWNER_ID] + (SUDO_ID if isinstance(SUDO_ID, list) else [SUDO_ID])

@VenomX.on_message(filters.command("stats") & filters.user(AUTHORIZED_USERS))
async def stats(cli: Client, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""ᴛᴏᴛᴀʟ sᴛᴀᴛs ᴏғ {(await cli.get_me()).mention} :

➻ **ᴄʜᴀᴛs :** {chats}
➻ **ᴜsᴇʀs :** {users}"""
    )
