"""Reminder Bot"""
import discord

# Grabs the bot token
with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()

# Starts the client
REMINDER_BOT = discord.Client()

@REMINDER_BOT.event
async def on_ready():
    print(f'{REMINDER_BOT.user} connected to discord : )')

# Runs the client
REMINDER_BOT.run(TOKEN)