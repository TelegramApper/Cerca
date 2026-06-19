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

STEP = 1.0

async def is_allowed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return False

    if user.id in ALLOWED_USER_IDS:
        logging.info("Allowed by user ID: %s", user.id)
        return True

    if chat.type == "private":
        return False

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}

        logging.info("Chat %s admins: %s", chat.id, admin_ids)
        logging.info("Checking user %s in admins", user.id)

        return user.id in admin_ids

    except Exception as e:
        logging.exception("Admin check failed in chat %s: %s", chat.id, e)
        return False

async def run_countdown(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        loop = asyncio.get_running_loop()
        start = loop.time()

        schedule = [
            (0.0, "3"),
            (STEP, "2"),
            (STEP * 2, "1"),
            (STEP * 3, "V"),
        ]

        for offset, text in schedule:
            wait_time = start + offset - loop.time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            logging.info("Sending %s to chat %s", text, chat_id)
            await context.bot.send_message(chat_id=chat_id, text=text)

        logging.info("Countdown finished in chat %s", chat_id)

    except Exception as e:
        logging.exception("Error inside countdown task: %s", e)

async def c_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_allowed(update, context):
            logging.info(
                "User not allowed: %s",
                update.effective_user.id if update.effective_user else "unknown"
            )
            return

        chat_id = update.effective_chat.id
        logging.info("Countdown started in chat %s", chat_id)

        context.application.create_task(run_countdown(chat_id, context))

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
