from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from config import PHOTO_PATH, CAPTION_TEXT, CHAT_LINK, RULES_LINK


async def handle_forwarded_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Комментарий под постом"""
    msg = update.message
    
    if not msg or not msg.is_automatic_forward:
        return
    
    try:
        with open(PHOTO_PATH, 'rb') as photo:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Чат", url=CHAT_LINK),
                InlineKeyboardButton("📋 Правила", url=RULES_LINK)
            ]])
            await msg.reply_photo(photo=photo, caption=CAPTION_TEXT, reply_markup=kb)
        print("✅ Комментарий отправлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def register_comments_handlers(app):
    app.add_handler(MessageHandler(filters.IS_AUTOMATIC_FORWARD, handle_forwarded_post), group=0)