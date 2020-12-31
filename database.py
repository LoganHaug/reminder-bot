import datetime

import pymongo

DB = pymongo.MongoClient().reminder_bot_db


def get_new_id(guild):
    """Gets a new auto-incremented id"""
    result = DB[guild].find({}).sort("_id", -1)
    if result.count() > 0:
        return result[0]["_id"] + 1
    return 0


def is_unique_reminder(guild, new_doc):
    """Ensures that a new reminder will be unique"""
    reminders = DB[guild].find({})
    for reminder in reminders:
        if reminder["reminder_text"] == new_doc["reminder_text"]:
            if reminder["date"] == new_doc["date"]:
                if reminder["channel"] == new_doc["channel"]:
                    return False
    return True    


def insert_reminder(
    guild, channel_id, year, month, day, hour, minutes, reminder_text, repeating
):
    """Inserts 1 reminder"""
    # Forms a datetime object with the user's date
    date = datetime.datetime(year, month, day, hour, minutes)
    new_doc = {
                "_id": get_new_id(guild),
                "guild": guild,
                "channel": channel_id,
                "date": date.timestamp(),
                "reminder_text": reminder_text,
                "repeating": repeating,
                "human_readable_time": date,
            }
    if date < datetime.datetime.now() or not is_unique_reminder(guild, new_doc):
        return False
    # Returns whether the write was successful or not
    return DB[str(guild)].insert_one(new_doc).acknowledged


def remove_reminder(reminder: dict):
    """Removes a reminder"""
    return DB[reminder["guild"]].delete_one(reminder).acknowledged


def get_reminders():
    """Returns a list of reminders to send messages for"""
    reminders = []
    for collection in DB.list_collection_names():
        for reminder in DB[collection].find({}):
            reminders.append(reminder)
    return reminders
