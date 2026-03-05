from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import database as db
from config import MAX_ADMINS, RANKS


async def setowner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if await db.has_owner(chat_id):
        if await db.is_owner(user_id, chat_id):
            await update.message.reply_text("👑 You are already Owner!")
        else:
            await update.message.reply_text("❌ This chat already has an Owner.")
        return
    
    await db.add_owner(user_id, chat_id)
    await db.set_rank(user_id, chat_id, 10)
    await update.message.reply_text("🏆 You are now the Owner!")


async def addadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_owner(user_id, chat_id):
        await update.message.reply_text("❌ Owner only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    count = await db.count_admins(chat_id)
    if count >= MAX_ADMINS:
        await update.message.reply_text(f"❌ Max {MAX_ADMINS} admins!")
        return
    
    target = update.message.reply_to_message.from_user
    await db.add_admin(target.id, chat_id, user_id)
    await db.set_rank(target.id, chat_id, 8)
    await update.message.reply_text(f"✅ {target.first_name} is now 🎖 Admin!")


async def removeadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_owner(user_id, chat_id):
        await update.message.reply_text("❌ Owner only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    target = update.message.reply_to_message.from_user
    await db.remove_admin(target.id, chat_id)
    await db.set_rank(target.id, chat_id, 1)
    await update.message.reply_text(f"✅ {target.first_name} is no longer Admin.")


async def adminlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    admins = await db.get_admins(chat_id)
    
    if not admins:
        await update.message.reply_text("📋 No admins yet.")
        return
    
    text = "┏━━━━━━━━━━━━━━━━━━━━┓\n"
    text += "┃ 🛡 **Bot Admins**\n"
    text += "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
    
    for i, admin in enumerate(admins, 1):
        text += f"{i}. `{admin['user_id']}`\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def setrank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if not await db.is_owner(user_id, chat_id):
        await update.message.reply_text("❌ Owner only.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message.")
        return
    
    try:
        rank_num = int(context.args[0])
        if rank_num < 1 or rank_num > 10:
            raise ValueError
    except:
        await update.message.reply_text(
            "❌ Use: `/setrank [1-10]`\n\nSee `/ranks` for list.",
            parse_mode='Markdown'
        )
        return
    
    target = update.message.reply_to_message.from_user
    await db.set_rank(target.id, chat_id, rank_num)
    await update.message.reply_text(
        f"✅ {target.first_name} → {RANKS[rank_num]}"
    )


async def ranks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
┏━━━━━━━━━━━━━━━━━━━━┓
┃ 🏆 **Available Ranks**
┗━━━━━━━━━━━━━━━━━━━━┛

`1` — 👤 User
`2` — ⭐ VIP
`3` — 💎 Premium

`4` — 🔰 Junior Moder
`5` — 🛡 Moder
`6` — ⚔️ Senior Moder

`7` — 📋 Junior Admin
`8` — 🎖 Admin
`9` — 👑 Senior Admin

`10` — 🏆 Owner

━━━━━━━━━━━━━━━━━━━━
Usage: `/setrank 5`
"""
    await update.message.reply_text(text, parse_mode='Markdown')


def register_admin_handlers(app):
    app.add_handler(CommandHandler("setowner", setowner_cmd))
    app.add_handler(CommandHandler("addadmin", addadmin_cmd))
    app.add_handler(CommandHandler("removeadmin", removeadmin_cmd))
    app.add_handler(CommandHandler("adminlist", adminlist_cmd))
    app.add_handler(CommandHandler("setrank", setrank_cmd))
    app.add_handler(CommandHandler("ranks", ranks_cmd))