from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
import random
import asyncio

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8210976690:AAE-y04U5qku2xAaxV0WRi1tGf2ulIRyeXA"
CHAT_LINK = "https://t.me/+tenQwnrH4XEwNTRi"
RULES_LINK = "https://t.me/+DKRrLd8xkiFmMGRi"
SOCIALS_LINK = "https://t.me/+ndgtra7-a0tiZDUy"
PHOTO_PATH = "mill.jpg"
CAPTION_TEXT = "Заходите в мой чатик 💝"
# ===================================================

pending_verification = {}


def generate_emoji_challenge():
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
    buttons = []
    for i, emoji in enumerate(challenge["options"]):
        buttons.append(
            InlineKeyboardButton(
                emoji,
                callback_data=f"verify_{user_id}_{i}_{challenge['correct']}"
            )
        )
    return InlineKeyboardMarkup([buttons])


# ==================== СПОСОБ 1: через new_chat_members ====================

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.new_chat_members:
        return

    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue

        await start_verification(context, message.chat_id, new_member, message)


# ==================== СПОСОБ 2: через chat_member update ====================

async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловим вход через chat_member апдейт"""

    result = update.chat_member
    if not result:
        return

    # Проверяем что человек именно ЗАШЁЛ в чат
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    print(f"📋 Chat member update: {old_status} -> {new_status}")

    # Если статус изменился на "member" (зашёл в чат)
    if old_status in ("left", "kicked") and new_status == "member":
        new_member = result.new_chat_member.user

        if new_member.is_bot:
            return

        await start_verification(context, result.chat.id, new_member, None)


# ==================== ОБЩАЯ ФУНКЦИЯ ВЕРИФИКАЦИИ ====================

async def start_verification(context, chat_id, new_member, reply_message=None):
    user_id = new_member.id
    user_name = new_member.first_name

    print(f"🔒 Новый участник: {user_name} (ID: {user_id})")

    # Мьютим
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
        print(f"🔇 Замьючен {user_name}")
    except Exception as e:
        print(f"❌ Не могу замьютить: {e}")
        return

    # Генерируем задание
    challenge = generate_emoji_challenge()
    keyboard = generate_new_keyboard(user_id, challenge)

    text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        f"🔒 Пройди верификацию чтобы писать в чат.\n\n"
        f"🎯 {challenge['text']}"
    )

    # Отправляем сообщение
    try:
        if reply_message:
            verify_msg = await reply_message.reply_text(
                text, parse_mode="HTML", reply_markup=keyboard
            )
        else:
            verify_msg = await context.bot.send_message(
                chat_id=chat_id, text=text,
                parse_mode="HTML", reply_markup=keyboard
            )

        pending_verification[user_id] = {
            "chat_id": chat_id,
            "message_id": verify_msg.message_id,
            "correct": challenge["correct"]
        }

        print(f"✅ Верификация отправлена для {user_name}")

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")


# ==================== КНОПКИ ВЕРИФИКАЦИИ ====================

async def handle_verification_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if user_id != target_user_id:
        await query.answer("❌ Это не твоя верификация!", show_alert=True)
        return

    chat_id = query.message.chat_id

    if chosen == correct:
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

        pending_verification.pop(user_id, None)

        await query.message.edit_text(
            f"✅ <b>{user_name}</b> прошёл верификацию! Добро пожаловать! 🎉",
            parse_mode="HTML"
        )
        await query.answer("✅ Верификация пройдена!")
        print(f"✅ {user_name} прошёл верификацию!")

        await asyncio.sleep(15)
        try:
            await query.message.delete()
        except:
            pass

    else:
        new_challenge = generate_emoji_challenge()
        new_keyboard = generate_new_keyboard(user_id, new_challenge)

        pending_verification[user_id]["correct"] = new_challenge["correct"]

        await query.message.edit_text(
            f"❌ Неправильно! Попробуй ещё раз, <b>{user_name}</b>\n\n"
            f"🎯 {new_challenge['text']}",
            parse_mode="HTML",
            reply_markup=new_keyboard
        )
        await query.answer("❌ Неправильно! Попробуй ещё раз")


# ==================== АВТО-КОММЕНТАРИИ ====================

async def handle_forwarded_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.is_automatic_forward:
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
                photo=photo, caption=CAPTION_TEXT, reply_markup=keyboard
            )
        print("✅ Комментарий добавлен!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


# ==================== ОТЛАДКА ====================

async def debug_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ВСЕ сообщения для отладки"""
    message = update.message
    if message:
        print(f"📨 Сообщение: type={message.chat.type}, "
              f"new_members={message.new_chat_members}, "
              f"text={message.text}, "
              f"from={message.from_user.first_name if message.from_user else 'None'}")


# ==================== ЗАПУСК ====================

def main():
    print("🚀 Бот запускается...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Отладка - показывает все сообщения в консоли
    app.add_handler(MessageHandler(filters.ALL, debug_all_messages), group=-1)

    # Способ 1: через new_chat_members
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_member
    ))

    # Способ 2: через chat_member update (нужно включить allowed_updates)
    app.add_handler(ChatMemberHandler(
        handle_chat_member_update,
        ChatMemberHandler.CHAT_MEMBER
    ))

    # Кнопки верификации
    app.add_handler(CallbackQueryHandler(
        handle_verification_button,
        pattern=r"^verify_"
    ))

    # Автокомментарии
    app.add_handler(MessageHandler(
        filters.IS_AUTOMATIC_FORWARD,
        handle_forwarded_post
    ))

    print("✅ Бот работает!")
    print("🔒 Верификация включена!")
    print("📋 Смотри консоль — там будет видно все события")

    # ВАЖНО: allowed_updates нужен чтобы ловить chat_member
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
