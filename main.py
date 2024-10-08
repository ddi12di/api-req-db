import os
import logging
from datetime import datetime
from config.config import DEFAULT_COMMANDS
from typing import List
import json
import time

from db.db import create_models, Request, db_save, User

from peewee import IntegrityError

from telebot.types import BotCommand, Message
from telebot import StateMemoryStorage, TeleBot
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter
from search import search
from search.search import search_id
from response_api.response import weather

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)


class UserInfo(StatesGroup):
    name = State()
    city = State()
    сurrent_weather = State()
    choice = State()


BOT_TOKEN = os.getenv('BOT_TOKEN')

state_storage = StateMemoryStorage()

bot = TeleBot(token=BOT_TOKEN, state_storage=state_storage)

with open('current.city.list.txt', encoding='utf8') as f:
    json_city = json.load(f)


def choice_state(text, message, city) -> None:
    bot.send_message(message.from_user.id, text)
    time.sleep(3)
    bot.send_message(message.from_user.id,
                     f'Что бы узнать в городе {city}\nТемпературу - 1\nПараметры ветра - 2\nГеоданные - 3\nСменить город - 4')
    bot.set_state(message.from_user.id, UserInfo.choice)
    return None


@bot.message_handler(commands=["start"])
def handle_start(message: Message) -> None:
    logger.info(message.from_user.username + ' send /start')
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name
        )
        bot.set_state(message.from_user.id, UserInfo.name, message.chat.id)
        bot.send_message(message.from_user.id, f'Привет, {message.from_user.username} введи свое имя')
    except IntegrityError:
        bot.send_message(message.from_user.id, 'Укажите, какой город интересует Вас ')
        bot.set_state(message.from_user.id, UserInfo.city, message.chat.id)


@bot.message_handler(state="*", commands=["history"])
def handle_tasks(message: Message) -> None:
    logger.info(message.from_user.username + ' send ' + message.text)

    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)

    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите /start")
        return

    req: List[Request] = user.users_backref.order_by(-Request.request_id).limit(10)
    result = []
    result.extend(map(str, reversed(req)))

    if not result:
        bot.send_message(message.from_user.id, "У вас еще нет запросов")
        return

    bot.send_message(message.from_user.id, "\n".join(result))
    bot.send_message(message.from_user.id, 'Укажите, какой город интересует Вас ')
    bot.set_state(message.from_user.id, UserInfo.city, message.chat.id)


@bot.message_handler(state=UserInfo.name)
def handle_cur_city(message: Message) -> None:
    logger.info(message.from_user.username + ' send ' + message.text)

    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Укажите, какой город интересует Вас ')
        bot.set_state(message.from_user.id, UserInfo.city, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text.capitalize()
            data['name_id'] = message.from_user.id
    else:
        bot.send_message(message.from_user.id, 'Имя может содеражать толко буквы')


@bot.message_handler(state=UserInfo.city)
def get_name(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['сity'] = message.text.capitalize()
        city = data['сity']
    logger.info(message.from_user.username + ' send ' + message.text)

    if message.text.isalpha():
        city_id = search_id(city)
        data['city_id'] = city_id
        if not city_id:
            bot.send_message(message.from_user.id, 'Город не найден попробуй еще раз')
            bot.set_state(message.chat.id, UserInfo.city)
        else:
            bot.send_message(message.from_user.id,
                             f'Что бы узнать в городе {city}\nТемпературу - 1\nПараметры ветра - 2\nГеоданные - 3\nСменить город - 4')
            bot.set_state(message.chat.id, UserInfo.choice)
    else:
        bot.send_message(message.from_user.id, 'Город может содеражать толко буквы')
        bot.set_state(message.chat.id, UserInfo.city)


@bot.message_handler(state=UserInfo.choice)
def choice(message: Message) -> None:
    logger.info(message.from_user.username + ' send ' + message.text)
    text_sorry = 'Извините, произошла ошибка ;( Попробуйте позже'

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['choice'] = message.text
        city = data['сity']
        choice_num = data['choice']
    w = weather(data['city_id'])
    db_save(w, message, choice)

    if w is None:
        bot.send_message(message.from_user.id, text_sorry)
    else:
        if choice_num == '2':
            text = f'Город - {w.city}\n ' \
                   f'Скорость ветра - {w.wind_speed}\n ' \
                   f'Град - {w.wind_deg}\n ' \
                   f'Порыв - {w.wind_gust}\n '
            choice_state(text, message, city)

        elif choice_num == '1':
            text = f'Город - {w.city}\n ' \
                   f'Температура - {w.temp}\n ' \
                   f'Ощущается температура - {w.feels_like}\n ' \
                   f'Давление - {w.pressure}\n '

            choice_state(text, message, city)
        elif choice_num == '4':
            bot.send_message(message.from_user.id, 'Укажите, какой город интересует Вас ')
            bot.set_state(message.from_user.id, UserInfo.city)

        elif choice_num == '3':
            text = f'Город - {w.city}\n ' \
                   f'Долгота - {w.lon}\n ' \
                   f'Широта - {w.lat}\n ' \
                   f'Страна - {w.country}\n '
            choice_state(text, message, city)

        else:
            bot.send_message(message.from_user.id,
                             f'Некорректный ввод\n'
                             f'Что бы узнать в городе {city}\nТемпературу - 1\nПараметры ветра - 2\nГеоданные - 3\nСменить город - 4')
            bot.set_state(message.chat.id, UserInfo.choice)


if __name__ == "__main__":
    create_models()
    bot.add_custom_filter(StateFilter(bot))
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
    bot.polling()
