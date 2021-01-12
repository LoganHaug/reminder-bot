import datetime

import pymongo

DB = pymongo.MongoClient().reminder_bot_db


def get_new_id(guild):
    """Gets a new auto-incremented id"""
    result = DB[guild + "_REMINDERS"].find({}).sort("_id", -1)
    if result.count() > 0:
        return result[0]["_id"] + 1
    return 0


def is_unique_reminder(guild, new_doc):
    """Ensures that a new reminder will be unique"""
    reminders = DB[guild + "_REMINDERS"].find({})
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
        "year": year,
        "month": month,
        "day": day,
        "reminder_text": reminder_text,
        "repeating": repeating,
        "human_readable_time": date,
    }
    if date < datetime.datetime.now() or not is_unique_reminder(guild, new_doc):
        return False
    # Returns whether the write was successful or not
    return DB[f"{guild}_REMINDERS"].insert_one(new_doc).acknowledged


def insert_operator(guild, user_id):
    """Inserts a document of a user that is an adminstrator"""
    return DB[f"{guild}_USERS"].insert_one({"_id": user_id}).acknowledged


def remove_reminder(reminder: dict):
    """Removes a reminder"""
    return DB[f'{reminder["guild"]}_REMINDERS'].delete_one(reminder).acknowledged


def get_reminders(guild=None, **query):
    """Returns a list of reminders to send messages for"""
    reminders = []
    if guild:
        for reminder in DB[f"{guild}_REMINDERS"].find(query):
            reminders.append(reminder)
    else:
        for collection in DB.list_collection_names():
            if collection[-10:] == "_REMINDERS":
                for reminder in DB[collection].find(query):
                    reminders.append(reminder)
    return reminders
