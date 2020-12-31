"""Reminder Bot"""
from discord.ext import commands
import pymongo
import yaml

import asyncio
import datetime
import threading
import time
from typing import Union

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


@REMINDER_BOT.command()
async def add_reminder(
    ctx,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    text: str,
    repeating: Union[str, bool] = False,
):
    """Attempts to add a reminder"""
    # Checks if the reminder should repeat, and if it is a valid interval
    if repeating and repeating not in conversion_dict:
        raise commands.UserInputError()
    # Tries to insert the reminder
    result = database.insert_reminder(
        ctx.guild.name,
        ctx.channel.id,
        year,
        month,
        day,
        hour,
        minute,
        text,
        repeating,
    )
    # Sends a status message, and restarts the reminders
    if result:
        # TODO: make the bot look pretty
        # TODO: confirm reminders with reactions
        asyncio.create_task(setup_reminders())
        await ctx.send("`Reminder stored, Pog`")
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
        await ctx.send(
            f"`Your input for the command was not correct, run {prefix}help add_reminder`"
        )
    else:
        await ctx.send(
            f"`An unexpected error has occured, run {prefix}help add_reminder`"
        )


# TODO: update command
# TODO: delete command


@REMINDER_BOT.event
async def on_ready():
    """Responds to when the bot readys"""
    # Setup the collections and reminders, print a status message
    asyncio.create_task(setup_reminders())
    print(f"{REMINDER_BOT.user} connected to discord : )")


# Runs the client
REMINDER_BOT.run(TOKEN)
