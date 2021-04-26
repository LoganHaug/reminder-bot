import datetime

import pymongo

DB = pymongo.MongoClient().reminder_bot_db


def get_new_id(guild):
    """Gets a new auto-incremented id"""
    result = DB[str(guild)].find({"type": "reminder"}).sort("reminder_id", -1)
    if result.count() > 0:
        return result[0]["reminder_id"] + 1
    return 0


def is_unique_reminder(guild, new_doc):
    """Ensures that a new reminder will be unique"""
    reminders = DB[str(guild)].find({"type": "reminder"})
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
        "type": "reminder",
        "reminder_id": get_new_id(guild),
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
    return DB[str(guild)].insert_one(new_doc).acknowledged


def insert_operator(guild: int, user_id: int) -> None:
    """Inserts a document of a user that is an adminstrator"""
    return DB[str(guild)].insert_one({"user_id": user_id, "type": "user"}).acknowledged


def increment_pat(guild: int, user_id: int) -> int:
    """Increments the number of pats for a user"""
    user = DB[str(guild)].find_one({"user_id": user_id, "type": "user"})
    if user is None:
        DB[str(guild)].insert_one({"user_id": user_id, "type": "user", "pats": 1})
        return 1
    if "pats" in user.keys():
        DB[str(guild)].update(user, {"$inc": {"pats": 1}})
        return user["pats"] + 1
    elif user is not None:
        DB[str(guild)].update(user, {"user_id": user_id, "type": "user", "pats": 1})
        return 1


def remove_reminder(reminder: dict):
    """Removes a reminder"""
    return DB[str(reminder["guild"])].delete_one(reminder).acknowledged


def get_reminders(guild: str=None, **query: dict) -> dict:
    """Returns a list of reminders to send messages for"""
    reminders = []
    query["type"] = "reminder"
    if guild:
        for reminder in DB[str(guild)].find(query):
            reminders.append(reminder)
    else:
        for collection in DB.list_collection_names():
            for reminder in DB[collection].find(query):
                reminders.append(reminder)
    return reminders

def award_karma(message, karma: int) -> None:
    """Awards karma to a user in a guild"""
    DB[str(message.guild.id)].update({"user_id": message.author.id, "type": "user"}, {"$inc": {"karma": karma}, "$set": {"name": message.author.name}}, upsert=True)