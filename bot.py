from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random
import asyncio

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8210976690:AAE-y04U5qku2xAaxV0WRi1tGf2ulIRyeXA"
CHAT_LINK = "https://t.me/+XNABfe8x8WY5ZGVi"
RULES_LINK = "https://t.me/+DKRrLd8xkiFmMGRi"
SOCIALS_LINK = "https://t.me/+ndgtra7-a0tiZDUy"
PHOTO_PATH = "mill.jpg"
CAPTION_TEXT = "Заходите в мой чатик 💝"
# ===================================================

# Хранилище данных верификации
pending_verification = {}


# ==================== ЭМОДЗИ ВЕРИФИКАЦИЯ ====================

def generate_emoji_challenge():
    """Генерируем задание с эмодзи"""

    emoji_sets = [
        {"question": "🐱", "name": "кота", "options": ["🐱", "🐶", "🐸", "🐷"]},
        {"question": "🌟", "name": "звезду", "options": ["🌙", "🌟", "☀️", "⭐"]},
        {"question": "🍎", "name": "яблоко", "options": ["🍊", "🍋", "🍎", "🍇"]},
        {"question": "🔥", "name": "огонь", "options": ["💧", "🔥", "❄️", "🌊"]},
        {"question": "💎", "name": "алмаз", "options": ["💎", "💰", "👑", "🏆"]},
        {"question": "🎵", "name": "музыку", "options": ["🎮", "🎵", "🎬", "📷"]},
        {"question": "🦋", "name": "бабочку", "options": ["🐝", "🐞", "🦋", "🐛"]},
        {"question": "🌈", "name": "радугу", "options": ["🌈", "🌪️", "⛈️", "🌤️"]},
        {"question": "🚀", "name": "ракету", "options": ["✈️", "🚁", "🚀", "🛸"]},
        {"question": "🎂", "name": "торт", "options": ["🍕", "🍔", "🌮", "🎂"]},
    ]

    challenge = random.choice(emoji_sets)
    correct_emoji = challenge["question"]
    options = challenge["options"][:]
    random.shuffle(options)

    correct_index = options.index(correct_emoji)

    return {
        "text": f"Найди {challenge['name']} {challenge['question']}",
        "options": options,
        "correct": correct_index
    }


def generate_new_keyboard(user_id, challenge):
    """Создаём клавиатуру для верификации"""
    buttons = []
    for i, emoji in enumerate(challenge["options"]):
        buttons.append(
            InlineKeyboardButton(
                emoji,
                callback_data=f"verify_{user_id}_{i}_{challenge['correct']}"
            )
        )
    return InlineKeyboardMarkup([buttons])


# ==================== ОБРАБОТКА НОВЫХ УЧАСТНИКОВ ====================

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Когда новый участник заходит в чат"""

    message = update.message
    if not message or not message.new_chat_members:
        return

    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue

        user_id = new_member.id
        chat_id = message.chat_id
        user_name = new_member.first_name

        # Мьютим пользователя
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_invite_users=False
                )
            )
        except Exception as e:
            print(f"❌ Не могу замьютить: {e}")
            return

        # Генерируем задание
        challenge = generate_emoji_challenge()
        keyboard = generate_new_keyboard(user_id, challenge)

        # Отправляем сообщение верификации
        verify_msg = await message.reply_text(
            f"👋 Привет, <b>{user_name}</b>!\n\n"
            f"🔒 Пройди верификацию чтобы писать в чат.\n\n"
            f"🎯 {challenge['text']}",
            parse_mode="HTML",
            reply_markup=keyboard
        )

        # Сохраняем данные
        pending_verification[user_id] = {
            "chat_id": chat_id,
            "message_id": verify_msg.message_id,
            "correct": challenge["correct"]
        }

        print(f"🔒 Верификация для {user_name} (ID: {user_id})")


# ==================== ОБРАБОТКА НАЖАТИЯ КНОПОК ====================

async def handle_verification_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем нажатие кнопки верификации"""

    query = update.callback_query
    data = query.data

    if not data.startswith("verify_"):
        return

    parts = data.split("_")
    target_user_id = int(parts[1])
    chosen = int(parts[2])
    correct = int(parts[3])

    user_id = query.from_user.id
    user_name = query.from_user.first_name

    # Только тот кто заходил может нажимать
    if user_id != target_user_id:
        await query.answer("❌ Это не твоя верификация!", show_alert=True)
        return

    chat_id = query.message.chat_id

    if chosen == correct:
        # ✅ ПРАВИЛЬНО — разрешаем писать
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True
                )
            )
        except Exception as e:
            print(f"❌ Ошибка размьюта: {e}")

        # Убираем из ожидающих
        pending_verification.pop(user_id, None)

        await query.message.edit_text(
            f"✅ <b>{user_name}</b> прошёл верификацию! Добро пожаловать! 🎉",
            parse_mode="HTML"
        )

        await query.answer("✅ Верификация пройдена!")
        print(f"✅ {user_name} прошёл верификацию!")

        # Удаляем сообщение через 15 секунд
        await asyncio.sleep(15)
        try:
            await query.message.delete()
        except:
            pass

    else:
        # ❌ НЕПРАВИЛЬНО — даём новую попытку
        new_challenge = generate_emoji_challenge()
        new_keyboard = generate_new_keyboard(user_id, new_challenge)

        # Обновляем данные
        pending_verification[user_id]["correct"] = new_challenge["correct"]

        await query.message.edit_text(
            f"❌ Неправильно! Попробуй ещё раз, <b>{user_name}</b>\n\n"
            f"🎯 {new_challenge['text']}",
            parse_mode="HTML",
            reply_markup=new_keyboard
        )

        await query.answer("❌ Неправильно! Попробуй ещё раз")
        print(f"❌ {user_name} ошибся, новая попытка")


# ==================== АВТО-КОММЕНТАРИИ ====================

async def handle_forwarded_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловим пост который переслался в группу комментариев"""

    message = update.message

    if not message:
        return

    if not message.is_automatic_forward:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Чат", url=CHAT_LINK),
            InlineKeyboardButton("📋 Правила", url=RULES_LINK)
        ],
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


# ==================== ЗАПУСК ====================

def main():
    print("🚀 Бот запускается...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_member
    ))

    app.add_handler(CallbackQueryHandler(
        handle_verification_button,
        pattern=r"^verify_"
    ))

    app.add_handler(MessageHandler(
        filters.IS_AUTOMATIC_FORWARD,
        handle_forwarded_post
    ))

    print("✅ Бот работает!")
    print("🔒 Верификация новых участников включена!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
