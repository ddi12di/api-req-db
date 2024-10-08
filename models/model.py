from dataclasses import dataclass


@dataclass
class Weather_model:
    temp: int
    feels_like: int
    pressure: int
    city: str
    description: str
    lon: int
    lat: int
    country: str
    wind_speed: int
    wind_deg: int
    wind_gust: int
