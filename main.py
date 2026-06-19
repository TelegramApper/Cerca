import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "")

ALLOWED_USER_IDS = {
    int(x.strip())
    for x in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if x.strip().isdigit()
}

async def is_allowed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return False

    if user.id in ALLOWED_USER_IDS:
        return True

    if chat.type == "private":
        return False

    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in ("administrator", "creator")

async def c_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update, context):
        return

    msg = update.effective_message
    await msg.reply_text("3")
    await asyncio.sleep(1)
    await msg.reply_text("2")
    await asyncio.sleep(1)
    await msg.reply_text("1")
    await asyncio.sleep(1)
    await msg.reply_text("v")

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("c", c_command))
    app.run_polling()

if __name__ == "__main__":
    main()
