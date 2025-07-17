import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from config import API_TOKEN
from db import create_tables
import handlers
from aiogram import F
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хендлеров

dp.message.register(handlers.cmd_start, Command("start"))
dp.message.register(handlers.cmd_quiz, F.text == "Начать игру")
dp.message.register(handlers.cmd_quiz, Command("quiz"))
dp.message.register(handlers.cmd_stats, Command("stats"))
dp.message.register(handlers.show_stats, F.text == "Показать ваш последний результат")
dp.callback_query.register(handlers.right_answer, F.data.startswith("right_answer"))
dp.callback_query.register(handlers.wrong_answer, F.data.startswith("wrong_answer"))

async def main():
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 