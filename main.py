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
    channel = REMINDER_BOT.get_channel(reminder["channel"])
    current_time = time.time()
    if reminder["date"] - current_time > 0:
        await asyncio.sleep(reminder["date"] - current_time)
        await channel.send(reminder["reminder_text"])
        if reminder["repeating"]:
            reminder_date = datetime.datetime.fromtimestamp(
                reminder["date"] + conversion_dict[reminder["repeating"]]
            )
            database.remove_reminder(reminder)
            try:
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
            except pymongo.errors.DuplicateKeyError:
                pass


async def setup_reminders():
    """Sets up the reminders"""
    tasks = []
    for reminder in database.get_reminders():
        tasks.append(asyncio.create_task(remind(reminder)))
    await asyncio.gather(*tasks)


@REMINDER_BOT.event
async def on_ready():
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
    try:
        if repeating and repeating not in conversion_dict:
            raise
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
        if result:
            await ctx.send("`Reminder stored, Pog`")
            asyncio.create_task(setup_reminders())
        else:
            await ctx.send("`Go yell at logan, it broke`")
    except:
        await ctx.send(f"`You malformed the command, use {prefix}help for help`")


# Runs the client
REMINDER_BOT.run(TOKEN)
