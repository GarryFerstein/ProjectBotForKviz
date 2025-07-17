import logging
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from quiz_data import quiz_data
from db import update_quiz_index, get_quiz_index, save_result, get_result

# Для хранения количества правильных ответов в сессии пользователя
user_correct_answers = {}

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer:{option}" if option == right_answer else f"wrong_answer:{option}")
        )
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    if current_question_index >= len(quiz_data):
        await message.answer("Вопросов больше нет. Квиз завершен!")
        return
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    user_correct_answers[user_id] = 0
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

# Хэндлер на команду /start
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="Начать игру"),
        types.KeyboardButton(text="Показать ваш последний результат")
    )
    builder.adjust(2)
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz и нажатие на кнопку
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# Хэндлер на команду /stats
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    result = await get_result(user_id)
    if result is not None:
        await message.answer(f"Ваш последний результат: {result} из {len(quiz_data)} правильных ответов.")
    else:
        await message.answer("Вы еще не проходили квиз.")

# Хэндлер на кнопку 'Показать ваш последний результат'
async def show_stats(message: types.Message):
    await cmd_stats(message)

# Callback для правильного ответа
async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Получаем выбранный вариант
    answer = callback.data.split(":", 1)[1]
    # Выводим ответ пользователя
    await callback.message.answer(f"Ваш ответ: {answer}\nВерно!")
    # Увеличиваем счетчик правильных ответов
    user_correct_answers[user_id] = user_correct_answers.get(user_id, 0) + 1
    current_question_index = await get_quiz_index(user_id)
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await save_result(user_id, user_correct_answers[user_id])
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {user_correct_answers[user_id]} из {len(quiz_data)}.")

# Callback для неправильного ответа
async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    answer = callback.data.split(":", 1)[1]
    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    correct_text = quiz_data[current_question_index]['options'][correct_option]
    await callback.message.answer(f"Ваш ответ: {answer}\nНеправильно. Правильный ответ: {correct_text}")
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await save_result(user_id, user_correct_answers.get(user_id, 0))
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {user_correct_answers.get(user_id, 0)} из {len(quiz_data)}.") 