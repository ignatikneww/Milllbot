from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
import database as db
from config import MAX_WARNINGS


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.ban_member(target.id)
        await update.message.reply_text(f"⛔️ {target.first_name} banned!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.unban_member(target.id)
        await update.message.reply_text(f"✅ {target.first_name} unbanned!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.unban_member(target.id)
        await update.message.reply_text(f"👢 {target.first_name} kicked!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        perms = ChatPermissions(can_send_messages=False)
        await update.effective_chat.restrict_member(target.id, perms)
        await update.message.reply_text(f"🔇 {target.first_name} muted!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await update.effective_chat.restrict_member(target.id, perms)
        await update.message.reply_text(f"🔊 {target.first_name} unmuted!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    warns = await db.add_warning(target.id, chat_id)
    
    if warns >= MAX_WARNINGS:
        await update.effective_chat.ban_member(target.id)
        await update.message.reply_text(
            f"⛔️ {target.first_name} — {warns}/{MAX_WARNINGS} warnings. Banned!"
        )
    else:
        await update.message.reply_text(
            f"⚠️ {target.first_name} — warning ({warns}/{MAX_WARNINGS})"
        )


async def unwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    await db.reset_warnings(target.id, chat_id)
    await update.message.reply_text(f"✅ {target.first_name} warnings cleared!")


async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id, chat_id):
        await update.message.reply_text("❌ Admins only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def register_moderation_handlers(app):
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("kick", kick_cmd))
    app.add_handler(CommandHandler("mute", mute_cmd))
    app.add_handler(CommandHandler("unmute", unmute_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("unwarn", unwarn_cmd))
    app.add_handler(CommandHandler("del", del_cmd))