import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from config import API_TOKEN
from db import create_tables
import handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хендлеров
dp.message.register(handlers.cmd_start, Command("start"))
dp.message.register(handlers.cmd_quiz, F.text == "Начать игру")
dp.message.register(handlers.cmd_quiz, Command("quiz"))
dp.message.register(handlers.cmd_stats, Command("stats"))
dp.message.register(handlers.show_stats, F.text == "Показать ваш последний результат")
dp.callback_query.register(handlers.handle_answer, F.data.startswith("answer"))

async def main():
    await create_tables()

    # Удаляем вебхук, если он установлен
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())