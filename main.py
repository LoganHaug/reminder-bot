"""Reminder Bot"""
from discord.ext import commands

import threading

import database

# Grabs the bot token
with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()

# Starts the client
REMINDER_BOT = commands.Bot(command_prefix='>')

def setup_daemons():
    """Sets up the reminder daemons"""
    pass

@REMINDER_BOT.event
async def on_ready():
    print(f'{REMINDER_BOT.user} connected to discord : )')
    setup_daemons()


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
