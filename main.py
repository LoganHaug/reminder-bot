"""Reminder Bot"""
from discord.ext import commands
import pymongo
import yaml

import asyncio
import datetime
import threading
import time
from typing import Union, Optional

import database


# Grabs the bot token
with open("token.txt", "r") as token_file:
    TOKEN = token_file.read()

# Loads the repeating interval dictionary
with open("conversions.yml", "r") as conversion_file:
    conversion_dict = yaml.load(conversion_file, Loader=yaml.Loader)


# Starts the client
prefix = ">"
REMINDER_BOT = commands.Bot(command_prefix=prefix)


async def remind(reminder: dict):
    """Execute one reminder"""
    # Check if the reminder is in the future
    if reminder["date"] - time.time() > 0:
        # Get the channel object to send the message
        channel = REMINDER_BOT.get_channel(reminder["channel"])
        # Wait until the reminder should go off
        await asyncio.sleep(reminder["date"] - time.time())
        # Send the reminder text in the channel
        await channel.send(reminder["reminder_text"])
        # Remove the reminder
        database.remove_reminder(reminder)
    # Schedules a repeating eminder
    if reminder["repeating"]:
        # Calculate when the next remidner should be
        reminder_date = datetime.datetime.fromtimestamp(
            reminder["date"] + conversion_dict[reminder["repeating"]]
        )
        # Remove the old reminder
        database.remove_reminder(reminder)
        # Add the new reminder
        database.insert_reminder(
            reminder["guild"],
            reminder["channel"],
            reminder_date.year,
            reminder_date.month,
            reminder_date.day,
            reminder_date.hour,
            reminder_date.minute,
            reminder["reminder_text"],
            reminder["repeating"],
        )
    # Remove a reminder that has passed
    else:
        database.remove_reminder(reminder)


async def setup_reminders():
    """Sets up the reminders"""
    # Stores all the reminder tasks
    tasks = []
    # Create tasks for all reminders, call the remind function
    for reminder in database.get_reminders():
        tasks.append(asyncio.create_task(remind(reminder)))
    # Run the tasks
    asyncio.gather(*tasks)


def split_date(date: str):
    """Splits a string date into year, month, day, and hour"""
    if "-" in date:
        split_date = date.strip().split("-")
    elif "/" in date:
        split_date = date.strip().split("/")
    return {
        "month": int(split_date[0]),
        "day": int(split_date[1]),
        "year": int(split_date[2]),
    }


def split_time(time: str):
    """Splits a string time into hour and minute"""
    time = time.strip().split(":")
    return {"hour": int(time[0]), "minute": int(time[1])}


@REMINDER_BOT.command(
    help="Date should be in month/day/year format, either with slashes or dashes (ex. month/day/year or month-day-year\n\nRepeating is an interval of time after which the reminder should be sent again, must be either daily, weekly, biweekly, or triweekly\n\nText is the text the reminder will be sent with, wrap with quotations if this contains whitespace"
)
async def add_reminder(
    ctx,
    date: str,
    time: str,
    text: str,
    repeating: Union[str, bool] = False,
):
    """Attempts to add a reminder"""
    # Checks if the reminder should repeat, and if it is a valid interval
    try:
        date = split_date(date)
        time = split_time(time)
    except UnboundLocalError:
        raise commands.UserInputError("Date or time was not in the correct format.")
    if repeating and repeating not in conversion_dict:
        raise commands.UserInputError()
    # Tries to insert the reminder
    result = database.insert_reminder(
        ctx.guild.name,
        ctx.channel.id,
        date["year"],
        date["month"],
        date["day"],
        time["hour"],
        time["minute"],
        text,
        repeating,
    )
    # Sends a status message, and restarts the reminders
    if result:
        # TODO: make the bot look pretty
        # TODO: confirm reminders with reactions
        asyncio.create_task(setup_reminders())
        # TODO: Make this a bit more verbose
        await ctx.send("```Reminder stored, Pog```")
    # This means the insertion of the reminder failed
    else:
        await ctx.send(
            "```This reminder already exists in the database or is not in the future```"
        )


@add_reminder.error
async def add_reminder_error(ctx, error):
    """Called when add_reminder() errors"""
    print(f"Bruh: {error}")
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"`{error} Run {prefix}help add_reminder`")
    elif isinstance(error, commands.errors.UserInputError):
        await ctx.send(f"`{error} Run {prefix}help add_reminder`")
    else:
        await ctx.send(
            f"`An unexpected error has occured, run {prefix}help add_reminder`"
        )


@REMINDER_BOT.command()
async def search_reminders(ctx, date: Optional[str] = None):
    """Searches for reminders on a specific day"""
    if date:
        try:
            date = split_date(date)
        except UnboundLocalError:
            await ctx.send("Date was not in the correct format.")
            return 1
        db_search = database.get_reminders(
            {"year": date["year"], "month": date["month"], "day": date["day"]}
        )
    else:
        db_search = database.get_reminders()
    message = ""
    for reminder in db_search:
        message += f'\n{reminder["_id"]}\t{reminder["month"]}/{reminder["day"]}/{reminder["year"]}\t{reminder["reminder_text"]}'
    await ctx.send(f"```Here are the reminders:\n{message}```")


@search_reminders.error
async def search_reminders_error(ctx, error):
    print(error)
    await ctx.send(
        f"```Something went wrong, try running {prefix}help search_reminders```"
    )


# TODO: update command


@REMINDER_BOT.command()
async def delete_reminder(ctx, index: int):
    """Deletes a reminder at a specific index"""
    search_result = database.get_reminders({"_id": index})
    if search_result != []:
        delete_result = database.remove_reminder(search_result[0])
        if delete_result:
            await ctx.send("```The reminder was successfully removed```")
        else:
            await ctx.send("```Something went wrong```")
    else:
        await ctx.send("```Could not find a reminder at this index```")


@REMINDER_BOT.event
async def on_ready():
    """Responds to when the bot readys"""
    # Setup the collections and reminders, print a status message
    asyncio.create_task(setup_reminders())
    print(f"{REMINDER_BOT.user} connected to discord : )")


# Runs the client
REMINDER_BOT.run(TOKEN)
