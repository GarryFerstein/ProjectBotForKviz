import logging
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from quiz_data import quiz_data
from db import update_quiz_index, get_quiz_state
from config import QUIZ_COVER_IMAGE_URL

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer:{option}:{'right' if option == right_answer else 'wrong'}"
        ))
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    state = await get_quiz_state(user_id)
    current_question_index = state["question_index"]
    if current_question_index >= len(quiz_data):
        await message.answer("Вопросов больше нет. Квиз завершен!")
        return
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    # Сбрасываем состояние: начальный индекс и счётчик
    await update_quiz_index(user_id, 0, 0)
    # Отправляем обложку квиза
    await message.answer_photo(
        photo=QUIZ_COVER_IMAGE_URL,
        caption="Добро пожаловать в квиз! Готовы проверить свои знания?",
        reply_markup=None
    )
    # Начинаем квиз
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

# Хэндлер на команду /quiz и кнопку
async def cmd_quiz(message: types.Message):
    await new_quiz(message)

# Хэндлер на команду /stats и кнопку
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    state = await get_quiz_state(user_id)
    total_questions = len(quiz_data)
    if state["question_index"] == 0 and state["correct_answers"] == 0:
        await message.answer("Вы ещё не проходили квиз.")
    else:
        await message.answer(f"Ваш последний результат: {state['correct_answers']} из {total_questions} правильных ответов.")

async def show_stats(message: types.Message):
    await cmd_stats(message)

# Обработка ответа
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data.split(":")
    selected_answer = data[1]
    result = data[2]

    # Убираем клавиатуру
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получаем текущее состояние
    state = await get_quiz_state(user_id)
    current_question_index = state["question_index"]
    correct_option_index = quiz_data[current_question_index]["correct_option"]
    correct_text = quiz_data[current_question_index]["options"][correct_option_index]

    if result == "right":
        await callback.message.answer(f"Ваш ответ: {selected_answer}\n✅ Верно!")
        new_correct_count = state["correct_answers"] + 1
    else:
        await callback.message.answer(f"Ваш ответ: {selected_answer}\n❌ Неправильно.\nПравильный ответ: {correct_text}")
        new_correct_count = state["correct_answers"]

    # Переходим к следующему вопросу
    next_question_index = current_question_index + 1

    if next_question_index < len(quiz_data):
        await update_quiz_index(user_id, next_question_index, new_correct_count)
        await get_question(callback.message, user_id)
    else:
        # Квиз завершён
        final_score = new_correct_count
        total_questions = len(quiz_data)
        await update_quiz_index(user_id, next_question_index, final_score)
        await callback.message.answer(f"🎉 Квиз завершён!\nВаш результат: {final_score} из {total_questions} правильных ответов.")