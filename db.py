import aiosqlite
from config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                correct_answers INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def update_quiz_index(user_id, index, correct_answers=0):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers)
            VALUES (?, ?, ?)
        ''', (user_id, index, correct_answers))
        await db.commit()

async def get_quiz_state(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT question_index, correct_answers FROM quiz_state WHERE user_id = ?
        ''', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                return {"question_index": result[0], "correct_answers": result[1]}
            else:
                return {"question_index": 0, "correct_answers": 0}