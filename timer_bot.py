import os
from dotenv import load_dotenv

import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
# Загружаем переменные из файла .env
load_dotenv()
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    button = InlineKeyboardButton("10 sec", callback_data="set_10")

    # Adding the button to the inline keyboard
    keyboard = [[button]]

    # Creating an inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Hi! Use /set <seconds> to set a timer", reply_markup=reply_markup)


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, defaultDue=None) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = defaultDue if defaultDue is not None else float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    match = re.search(r"set_(\d+)", query.data)
    
    if match:
        await set_timer(update, context, int(match.group(1)))
    # else:
    #     return None  # Если "set_x" не найдено, возвращаем None


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()