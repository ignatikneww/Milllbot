from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import database as db
from config import RANKS, RANKS_SHORT
import time


async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    user_data = await db.get_user(user.id, chat_id)
    
    if not user_data:
        await update.message.reply_text("❌ Send a message first!")
        return
    
    rank = RANKS.get(user_data['rank'], "👤 User")
    reg_date = time.strftime('%d.%m.%Y', time.localtime(user_data['first_seen']))
    
    text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃ 📱 **{user.first_name}**
┗━━━━━━━━━━━━━━━━━━━━┛

🏆 **Rank:** {rank}

📊 **Statistics:**
├ Messages: `{user_data['messages_count']}`
├ Warnings: `{user_data['warnings']}/3`
└ Joined: `{reg_date}`
"""
    await update.message.reply_text(text, parse_mode='Markdown')


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    top_users = await db.get_top_users(chat_id, 10)
    
    if not top_users:
        await update.message.reply_text("📊 No data yet.")
        return
    
    text = "🏆 **Top 10 Users**\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, user in enumerate(top_users):
        medal = medals[i] if i < 3 else f"`{i+1}.`"
        rank = RANKS_SHORT.get(user['rank'], "User")
        name = user['first_name'] or "Anonymous"
        text += f"{medal} **{name}**\n"
        text += f"    └ {user['messages_count']} msgs • {rank}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    chat_stats = await db.get_chat_stats(chat_id)
    total_users = await db.get_total_users(chat_id)
    admin_count = await db.count_admins(chat_id)
    
    total_msg = chat_stats['total_messages'] if chat_stats else 0
    
    text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃ 📊 **Chat Statistics**
┗━━━━━━━━━━━━━━━━━━━━┛

👥 Users: `{total_users}`
💬 Messages: `{total_msg}`
🛡 Admins: `{admin_count}/10`
"""
    await update.message.reply_text(text, parse_mode='Markdown')


async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await db.add_user(user.id, chat_id, user.username or "", user.first_name or "")
    await db.add_message(user.id, chat_id)


def register_stats_handlers(app):
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("top", top_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, log_message), group=99)