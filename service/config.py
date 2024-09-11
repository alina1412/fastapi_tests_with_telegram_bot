import datetime
from os import environ

import pytz
from dotenv import load_dotenv

load_dotenv()
key = environ.get("key")
assert key

db_settings = {
    "db_name": environ.get("DB_NAME"),
    "db_host": environ.get("DB_HOST"),
    "db_user": environ.get("DB_USERNAME"),
    "db_port": environ.get("DB_PORT"),
    "db_password": environ.get("DB_PASSWORD"),
}


def utcnow() -> datetime:
    """datetime object with timezone awareness"""
    now: datetime = datetime.datetime.now(tz=pytz.utc)
    return now
