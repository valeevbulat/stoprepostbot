import os
from dotenv import load_dotenv

import logging
import json
import re

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# Загружаем переменные из файла .env
load_dotenv()

# Получаем токен из переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Функция для обработки команд
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я буду фильтровать сообщения.")

# Функция для фильтрации сообщений
async def filter_message(update: Update, context: CallbackContext):
    if update.message.via_bot is not None:
        username = update.message.via_bot.username
        print(update.message)
        # pretty_data = json.dumps(update.message, indent=4)
        # print(pretty_data)
        # message = update.message.text
        # # Пример фильтрации сообщений с использованием ключевых слов
        # logging.info(update)
        # print(f"Получено сообщение: {message}")
        if "catteaaibot" in username.lower():
            await update.message.delete()  # Удаление сообщения, если в нем слово "спам"
            # await update.message.reply_text("Сообщение удалено, потому что оно содержит спам.")
        # else:
            # print(f"Получено сообщение: {message}")

def main():
    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчика команд
    application.add_handler(CommandHandler("start", start))

    # Добавление обработчика для сообщений
    application.add_handler(MessageHandler(filters.ALL, filter_message))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()