import os
from datetime import datetime
from peewee import IntegrityError

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    IntegerField,
    Model,
    SqliteDatabase,
    DateField,
    ForeignKeyField
)

DB_PATH = os.getenv('DB_PATH')
DATE_FORMAT = os.getenv('DATE_FORMAT')

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()


class Request(BaseModel):
    request_id = IntegerField(primary_key=True)
    id = ForeignKeyField(User, backref="users_backref")
    username = CharField()
    firstname = CharField()
    date = DateField()
    time = CharField()
    choice = CharField()
    city = CharField()
    temp = CharField()
    lon = CharField()
    lat = CharField()
    country = CharField()
    wind_speed = CharField()
    wind_deg = CharField()
    wind_gust = CharField()

    def __str__(self):
        return " {date} - {time} - {username} - {city} ".format(
            city=self.city,
            date=self.date,
            time=self.time,
            username=self.username,
        )


def db_save(w, message, choice) -> None:
    req = Request.create(
        username=message.from_user.username,
        id=message.from_user.id,
        firstname=message.from_user.first_name,
        city=w.city,
        temp=w.temp,
        date=datetime.now().date(),
        time=datetime.now().time().strftime("%H:%M"),
        lon=w.lon,
        lat=w.lat,
        country=w.country,
        wind_speed=w.wind_speed,
        wind_deg=w.wind_deg,
        wind_gust=w.wind_gust,
        choice=choice
    )
    req.save()


def create_models():
    db.create_tables(BaseModel.__subclasses__())
