import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения  не загружены т.к отсутствует файл(ы) .env")
else:

    load_dotenv()
    URL = os.getenv('URL')
    URL_OTHER = os.getenv('URL_OTHER')
    TOKEN = os.getenv('TOKEN')


DEFAULT_COMMANDS = (
    ("start", "Начать работу"),
    ("history", "История запросов"),
)

