import datetime

import pymongo

DB = pymongo.MongoClient().reminder_bot_db

def setup_collections():
    """Sets up unique indexes on all collections"""
    for collection in DB.list_collection_names():
        DB[collection].create_index([("channel", 1), ("date", 1), ("reminder_text", 1), ("repeating", 1)], unique=True)

def insert_reminder(guild, channel_id, year, month, day, time, reminder_text, repeating=False):
    """Inserts 1 reminder"""
    date = datetime.datetime(int(year), int(month), int(day), int(time))
    return DB[str(guild)].insert_one({
        "channel": channel_id,
        "date": date.timestamp(),
        "reminder_text": reminder_text,
        "repeating": False
    }).acknowledged

def get_reminders():
    """Returns a list of reminders to send messages for"""
    reminders = []
    for collection in DB.list_collection_names():
        for reminder in DB[collection].find({}):
            del reminder["_id"]
            reminders.append(reminder)
    return reminders
