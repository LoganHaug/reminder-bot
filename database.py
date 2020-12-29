import datetime

import pymongo

DB = pymongo.MongoClient().reminder_bot_db


def setup_collections():
    """Sets up unique indexes on all collections"""
    # Iterates through all collections, enforces uniqueness
    for collection in DB.list_collection_names():
        DB[collection].create_index(
            [("channel", 1), ("date", 1), ("reminder_text", 1), ("repeating", 1)],
            unique=True,
        )


def insert_reminder(
    guild, channel_id, year, month, day, hour, minutes, reminder_text, repeating
):
    """Inserts 1 reminder"""
    # Forms a datetime object with the user's date
    date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
    # Returns whether the write was successful or not
    return (
        DB[str(guild)]
        .insert_one(
            {
                "guild": guild,
                "channel": channel_id,
                "date": date.timestamp(),
                "reminder_text": reminder_text,
                "repeating": repeating,
                "human_readable_time": date,
            }
        )
        .acknowledged
    )


def remove_reminder(reminder: dict):
    """Removes a reminder"""
    return DB[reminder["guild"]].delete_one(reminder).acknowledged


def get_reminders():
    """Returns a list of reminders to send messages for"""
    reminders = []
    for collection in DB.list_collection_names():
        for reminder in DB[collection].find({}):
            # Deletes the premade _id field from mongodb
            del reminder["_id"]
            reminders.append(reminder)
    return reminders
