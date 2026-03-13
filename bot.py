from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8210976690:AAE-y04U5qku2xAaxV0WRi1tGf2ulIRyeXA"
CHAT_LINK = "https://t.me/+XNABfe8x8WY5ZGVi"
RULES_LINK = "https://t.me/+DKRrLd8xkiFmMGRi"
SOCIALS_LINK = "https://t.me/+ndgtra7-a0tiZDUy"  # Все соц сети
PHOTO_PATH = "mill.jpg"
CAPTION_TEXT = "Заходите в мой чатик 💝"
# ===================================================


async def handle_forwarded_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловим пост который переслался в группу комментариев"""

    message = update.message

    if not message:
        return

    if not message.is_automatic_forward:
        return

    keyboard = InlineKeyboardMarkup([
        # Первый ряд - две кнопки рядом
        [
            InlineKeyboardButton("💬 Чат", url=CHAT_LINK),
            InlineKeyboardButton("📋 Правила", url=RULES_LINK)
        ],
        # Второй ряд - одна большая кнопка на всю ширину
        [
            InlineKeyboardButton("🌐 Все ссылки и соц сети", url=SOCIALS_LINK)
        ]
    ])

    try:
        with open(PHOTO_PATH, 'rb') as photo:
            await message.reply_photo(
                photo=photo,
                caption=CAPTION_TEXT,
                reply_markup=keyboard
            )
        print("✅ Комментарий добавлен!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    print("🚀 Бот запускается...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(
        filters.IS_AUTOMATIC_FORWARD,
        handle_forwarded_post
    ))

    print("✅ Бот работает!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
