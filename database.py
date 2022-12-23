import datetime

import sqlite3 

DB = sqlite3.connect("reminder_bot.db") 
cursor = DB.cursor()

# Check if user and reminder tables exist
tables = cursor.execute("""SELECT name FROM sqlite_master 
                           WHERE type='table';""").fetchall()

if ("users",) not in tables:
    cursor.execute("""CREATE TABLE users 
                      (user_id INTEGER,
                      id INTEGER PRIMARY KEY AUTOINCREMENT);""")

if ("reminders",) not in tables:
    cursor.execute("""CREATE TABLE reminders
                      (reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date INTEGER,
                       channel INTEGER,
                       reminder_text TEXT,
                       repeating INTEGER,
                       guild INTEGER);""")


def _create_where_query(doc):
    # this is a security risk
    query = "WHERE " 
    for key, value in doc:
        query.append(f"{str(key)}={str(value)}, ")
    return query[:-2]

def _is_unique_reminder(guild, new_doc):
    """Ensures that a new reminder will be unique"""
    reminders = cursor.execute("SELECT * from reminders").fetchall()
    for reminder in reminders:
        if reminder[4] == new_doc["reminder_text"] and reminder[1] == new_doc["date"] and reminder[3] == new_doc["channel"]:
            return False
    return True

def _tuple_to_dict(tup: tuple) -> dict:
    if len(tup) == 2:
        return {"user_id": tup[0], "id": tup[1]}
    elif len(tup) == 6:
        return {"reminder_id": tup[0], "date": tup[1], "channel": tup[2], "reminder_text": tup[3], "repeating": tup[4], "guild": tup[5]}
    else:
        raise IndexError("Tuple did not have the expected number of indicies (2 or 6)")

def _dict_to_tuple(d: dict) -> tuple:
    if len(d) == 2:
        return (d["user_id"], d["id"])
    elif len(d) == 6:
        return (d["reminder_id"], d["date"], d["channel"], d["reminder_text"], d["repeating"], d["guild"])
    else:
        raise KeyError("Dictionary did not have the expected number of keys (2 or 6)")

def insert_reminder(
    guild, channel_id, year, month, day, hour, minutes, reminder_text, repeating
):
    """Inserts 1 reminder"""
    # Forms a datetime object with the user's date
    date = datetime.datetime(year, month, day, hour, minutes)
    # Create a new row
    nr = {
        "guild": guild,
        "channel": channel_id,
        "date": date.timestamp(),
        "reminder_text": reminder_text,
        "repeating": repeating,
    }
    if date < datetime.datetime.now() or not _is_unique_reminder(guild, nr):
        return False
    # Returns whether the write was successful or not
    try:
        cursor.execute(f"""INSERT INTO reminders 
                          (date, channel, reminder_text, repeating, guild)
                          VALUES ({nr['date']}, {nr['channel']}, nr['reminder_text'], nr['repeating']);""")
        return True
    except Exception as e:
        print("Error inserting reminder")
        print(e)
        return False

def insert_operator(guild: int, user_id: int) -> None:
    """Inserts a document of a user that is an adminstrator"""
    try:
        cursor.execute(f"""INSERT INTO users (user_id)
                          VALUES ({user_id});""")
        return True

    except Exception as e:
        print("Error inserting operator")
        print(e)
        return False

def remove_reminder(reminder: dict):
    """Removes a reminder"""
    try:
        cursor.execute("DELETE FROM reminders " + _create_where_query(reminder))
        return True
    except Exception as e:
        print("Error removing reminder from db")
        print(e)
        return False


def get_reminders(guild: int = None, **query: dict) -> list:
    """Returns a list of reminders to send messages for"""
    if guild:
        statement = "SELECT * FROM reminders where guild = ?"
    elif query != {}:
        statement = "SELECT * from reminders " + _create_where_query(query)
    else:
        statement = "SELECT * FROM reminders"

    return [_tuple_to_dict(r) for r in cursor.execute(statement).fetchall()]

