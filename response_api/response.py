import requests
import logging

from config.config import URL, TOKEN, URL_OTHER

from dotenv import load_dotenv
import os
import json
from models.model import Weather_model

logger = logging.getLogger(__name__)

load_dotenv()


def weather(key: int) -> dict:
    response = requests.post(URL + f"{key}" + "&appid=" + TOKEN + URL_OTHER)
    # 200 - 299 - OK
    # 300 - 399 - Redirect
    # 400 - 499 - Client error
    # 500 - 599 - Server error

    if response.status_code != 200:
        logger.error(f'Status code:{response.status_code}, Error: {response.text}')
        return None

    all_response = response.json()

    #     all_response = {
    #   "coord": {
    #     "lon": 39.4139,
    #     "lat": 57.1914
    #   },
    #   "weather": [
    #     {
    #       "id": 801,
    #       "main": "Clouds",
    #       "description": "небольшая облачность",
    #       "icon": "02n"
    #     }
    #   ],
    #   "base": "stations",
    #   "main": {
    #     "temp": 14.46,
    #     "feels_like": 13.84,
    #     "temp_min": 14.46,
    #     "temp_max": 14.46,
    #     "pressure": 1032,
    #     "humidity": 72,
    #     "sea_level": 1032,
    #     "grnd_level": 1017
    #   },
    #   "visibility": 10000,
    #   "wind": {
    #     "speed": 2.25,
    #     "deg": 140,
    #     "gust": 2.32
    #   },
    #   "clouds": {
    #     "all": 23
    #   },
    #   "dt": 1726512767,
    #   "sys": {
    #     "country": "RU",
    #     "sunrise": 1726455326,
    #     "sunset": 1726501143
    #   },
    #   "timezone": 10800,
    #   "id": 501183,
    #   "name": "Ростов",
    #   "cod": 200
    # }

    temp = all_response['main']['temp']
    feels_like = all_response['main']['feels_like']
    pressure = all_response['main']['pressure']
    city = all_response['name']
    description = all_response['weather'][0]['description']
    lon = all_response['coord']['lon']
    lat = all_response['coord']['lat']
    country = all_response['sys']['country']
    wind_speed = all_response['wind']['speed']
    wind_deg = all_response['wind']['deg']
    wind_gust = all_response['wind']['gust']

    w = Weather_model(temp, feels_like, pressure, city, description, lon, lat, country, wind_speed, wind_deg, wind_gust)

    return w
