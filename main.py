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


async def setup_reminders():
    """Sets up the reminders"""
    # Stores all the reminder tasks
    tasks = []
    # Create tasks for all reminders, call the remind function
    for reminder in database.get_reminders():
        tasks.append(asyncio.create_task(remind(reminder)))
    # Run the tasks
    asyncio.gather(*tasks)


@REMINDER_BOT.event
async def on_ready():
    """Responds to when the bot readys"""
    # Setup the collections and reminders, print a status message
    database.setup_collections()
    asyncio.create_task(setup_reminders())
    print(f"{REMINDER_BOT.user} connected to discord : )")


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
    try:
        # Checks if the reminder should repeat, and if it is a valid interval
        if repeating and repeating not in conversion_dict:
            raise
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
            await ctx.send("`Reminder stored, Pog`")
            asyncio.create_task(setup_reminders())
        # This means the insertion of the reminder failed
        else:
            await ctx.send("`Go yell at logan, it broke`")
    # TODO: catch specific errors
    # User Errors
    except:
        await ctx.send(f"`You malformed the command, use {prefix}help for help`")


# Runs the client
REMINDER_BOT.run(TOKEN)
