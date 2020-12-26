"""Reminder Bot"""
from discord.ext import commands

import asyncio
import threading
import time

import database

# Grabs the bot token
with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()

# Starts the client
REMINDER_BOT = commands.Bot(command_prefix='>')

def remind(reminder: dict):
    """Execute one reminder"""
    channel = REMINDER_BOT.get_channel(reminder["channel"])
    current_time = time.time()
    if reminder["date"] - current_time > 0:
        time.sleep(reminder["date"] - current_time)
        hannel.send(reminder["reminder_text"])

async def setup_reminders():
    """Sets up the reminder daemons"""
    for reminder in database.get_reminders():
        remind(reminder)
    print(1)

@REMINDER_BOT.event
async def on_ready():
    print(f'{REMINDER_BOT.user} connected to discord : )')
    database.setup_collections()
    await setup_reminders()


@REMINDER_BOT.command()
async def add_reminder(ctx, year, month, day, time, text):
    try:
        result = database.insert_reminder(ctx.guild, ctx.channel.id, year, month, day, time, text)
        if result:
            await ctx.send("`Reminder stored, Pog`")
            await setup_daemons()
        else:
            await ctx.send("`Go yell at logan, it broke`")
    except:
        await ctx.send("`You messed up lol`")

# Runs the client
REMINDER_BOT.run(TOKEN)
