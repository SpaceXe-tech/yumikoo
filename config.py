from os import getenv

from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
API_ID = int(getenv("API_ID", 27353035))
API_HASH = getenv("API_HASH", "cf2a75861140ceb746c7796e07cbde9e")
BOT_TOKEN = getenv("BOT_TOKEN", None)

# Owner and Sudo users
OWNER_ID = int(getenv("OWNER_ID", "7403602903"))
SUDO_ID = getenv("SUDO_ID", "5960968099")  # Can be a single ID or comma-separated list

# MongoDB URL
MONGO_URL = getenv("MONGO_URL", None)

# Support group and update channel (case-insensitive handling)
SUPPORT_GRP = getenv("SUPPORT_GRP", "friends_mansion").lower()
UPDATE_CHNL = getenv("UPDATE_CHNL", "BillaSpace").lower()

# Owner username (case-insensitive handling)
OWNER_USERNAME = getenv("OWNER_USERNAME", "oye_anurag").lower()

# Random Start Images
IMG = [
    "https://graph.org/file/74f44dc0a7be7898000eb-ca93537c21ba18965b.jpg",
    "https://graph.org/file/1f22efab7f7ca602d5ade-9250b0f4e1f48a4329.jpg",
    "https://graph.org/file/c25eea258b1c5e5bd48f1-91ab110884ff37cdf6.jpg",
    "https://graph.org/file/ed0132caf87095f98d3de-10f330e1dd13813fe2.jpg",
    "https://graph.org/file/7374e2f209a17d25f290f-13bcb2b06109779778.jpg",
    "https://graph.org/file/53e0497c7caf79e17bcbe-43903e61e1ae6c4322.jpg",
    "https://graph.org/file/79ed43b49ec6084e6bcbd-c1f462364c2d5095e6.jpg",
    "https://graph.org/file/f303d270e13a42925642f-799b78db83059d071c.jpg",
    "https://graph.org/file/02cce16596a5bfb00bf71-b6cccb67c1cdb51f62.jpg",
    "https://graph.org/file/42c8e78706c3e50895a2d-464ac7c97cf0969b4f.jpg",
    "https://graph.org/file/e28022070e01cc6393a18-3f368987a811ff0155.jpg",
    "https://graph.org/file/0c963960112c7a2007a2c-b7cce508a84e9a6808.jpg",
    "https://graph.org/file/255aca80762062243de10-0fc71c5250b650a83a.jpg",
    "https://graph.org/file/7debda6e69b87b94aad0a-0aa2ed9096aa7a1781.jpg",
    "https://telegra.ph//file/e05d6e4faff7497c5ae56.jpg",
    "https://telegra.ph//file/1e54f0fff666dd53da66f.jpg",
    "https://telegra.ph//file/18e98c60b253d4d926f5f.jpg",
    "https://telegra.ph//file/b1f7d9702f8ea590b2e0c.jpg",
    "https://telegra.ph//file/7bb62c8a0f399f6ee1f33.jpg",
    "https://telegra.ph//file/dd00c759805082830b6b6.jpg",
    "https://telegra.ph//file/3b996e3241cf93d102adc.jpg",
    "https://telegra.ph//file/610cc4522c7d0f69e1eb8.jpg",
    "https://telegra.ph//file/bc97b1e9bbe6d6db36984.jpg",
    "https://telegra.ph//file/2ddf3521636d4b17df6dd.jpg",
    "https://telegra.ph//file/72e4414f618111ea90a57.jpg",
    "https://graph.org/file/95ab943942d25371d0254-f1f1bfadd5f23e7dfd.jpg",
    "https://telegra.ph//file/0afd9c2f70c6328a1e53a.jpg",
    "https://telegra.ph//file/82ff887aad046c3bcc9a3.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/a7cba6e78bb63e1b4aefb.jpg",
    "https://telegra.ph//file/f8ba75bdbb9931cbc8229.jpg",
    "https://telegra.ph//file/07bb5f805178ec24871d3.jpg",
    "https://telegra.ph/file/ec0ed654f5f5cefc90f95.jpg",
    "https://telegra.ph/file/f6aa2a3659462401cb600.jpg",
    "https://telegra.ph/file/0c3d91bcf75524a844883.jpg",
    "https://telegra.ph/file/6c5df27e71e074f1c7123.jpg",
    "https://telegra.ph/file/ff2ddc282fe7868e3cf73.jpg",
    "https://telegra.ph/file/6130ea9373d5f60898a52.jpg",
    "https://telegra.ph/file/45e5da1eab8f5892981ca.jpg",
]


# Random Stickers
STICKER = [
    "CAACAgUAAx0CYlaJawABBy4vZaieO6T-Ayg3mD-JP-f0yxJngIkAAv0JAALVS_FWQY7kbQSaI-geBA",
    "CAACAgUAAx0CYlaJawABBy4rZaid77Tf70SV_CfjmbMgdJyVD8sAApwLAALGXCFXmCx8ZC5nlfQeBA",
    "CAACAgUAAx0CYlaJawABBy4jZaidvIXNPYnpAjNnKgzaHmh3cvoAAiwIAAIda2lVNdNI2QABHuVVHgQ",
]


EMOJIOS = [
    "💣",
    "💥",
    "🎶",
    "🧨",
    "⚡",
    "💟",
    "👻",
    "💜",
    "🎩",
    "🕊",
]
