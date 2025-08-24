import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME")
QUIZ_COVER_IMAGE_URL = os.getenv("QUIZ_COVER_IMAGE_URL", "https://storage.yandexcloud.net/quiz-bot-cover/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-17%20%D0%B2%2019.41.08.png")  # URL изображения