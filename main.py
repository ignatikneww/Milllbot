from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import database as db
from config import BOT_TOKEN
from handlers import register_all_handlers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
┏━━━━━━━━━━━━━━━━━━━━┓
┃ 👋 **Welcome to MillBot!**
┗━━━━━━━━━━━━━━━━━━━━┛

📋 `/help` — all commands
👤 `/profile` — your profile
🏆 `/top` — top users
🎖 `/ranks` — rank list

━━━━━━━━━━━━━━━━━━━━
👑 First time? Use `/setowner`
"""
    await update.message.reply_text(text, parse_mode='Markdown')


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
┏━━━━━━━━━━━━━━━━━━━━┓
┃ ⚡️ **MillBot Commands**
┗━━━━━━━━━━━━━━━━━━━━┛

👤 **Everyone:**
├ `/profile` — your profile
├ `/top` — top users
├ `/stats` — chat stats
└ `/ranks` — rank list

🛡 **Admins:**
├ `/ban` — ban user
├ `/unban` — unban user
├ `/kick` — kick user
├ `/mute` — mute user
├ `/unmute` — unmute user
├ `/warn` — add warning
├ `/unwarn` — clear warnings
└ `/del` — delete message

👑 **Owner:**
├ `/setrank [1-10]` — set rank
├ `/addadmin` — add admin
├ `/removeadmin` — remove admin
└ `/adminlist` — admin list
"""
    await update.message.reply_text(text, parse_mode='Markdown')


async def post_init(application):
    await db.init_db()
    print("✅ Bot started!")


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    
    register_all_handlers(app)
    
    print("🚀 Starting MillBot...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()