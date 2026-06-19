import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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
    try:
        if not await is_allowed(update, context):
            logging.info("User not allowed: %s", update.effective_user.id if update.effective_user else "unknown")
            return

        msg = update.effective_message
        chat_id = update.effective_chat.id

        logging.info("Countdown started in chat %s", chat_id)

        await msg.reply_text("3")
        await asyncio.sleep(1)

        logging.info("Sending 2 to chat %s", chat_id)
        await context.bot.send_message(chat_id=chat_id, text="2")
        await asyncio.sleep(1)

        logging.info("Sending 1 to chat %s", chat_id)
        await context.bot.send_message(chat_id=chat_id, text="1")
        await asyncio.sleep(1)

        logging.info("Sending v to chat %s", chat_id)
        await context.bot.send_message(chat_id=chat_id, text="v")

        logging.info("Countdown finished in chat %s", chat_id)

    except Exception as e:
        logging.exception("Error inside /c command: %s", e)

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("c", c_command))
    app.run_polling()

if __name__ == "__main__":
    main()
