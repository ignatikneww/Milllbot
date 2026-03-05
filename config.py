import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_LINK = os.getenv("CHAT_LINK")
RULES_LINK = os.getenv("RULES_LINK")

PHOTO_PATH = "mill.jpg"
CAPTION_TEXT = "💝 Заходите в мой чатик 💝"

MAX_ADMINS = 10
MAX_WARNINGS = 3

# 10 рангов
RANKS = {
    1: "👤 User",
    2: "⭐ VIP",
    3: "💎 Premium",
    4: "🔰 Junior Moder",
    5: "🛡 Moder",
    6: "⚔️ Senior Moder",
    7: "📋 Junior Admin",
    8: "🎖 Admin",
    9: "👑 Senior Admin",
    10: "🏆 Owner"
}

# Короткие версии для топа
RANKS_SHORT = {
    1: "User",
    2: "VIP",
    3: "Premium",
    4: "Jr.Moder",
    5: "Moder",
    6: "Sr.Moder",
    7: "Jr.Admin",
    8: "Admin",
    9: "Sr.Admin",
    10: "Owner"
}