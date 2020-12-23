import datetime

from pymongo import MongoClient

DB = MongoClient().reminder_bot_db

def insert_reminder(guild, channel_id, year, month, day, time, reminder_text, repeating=False):
    date = datetime.datetime(int(year), int(month), int(day), int(time))
    return DB[str(guild)].insert_one({
        'channel': channel_id,
        'date': date.timestamp(),
        'reminder_text': reminder_text,
        'repeating': False
    }).acknowledged