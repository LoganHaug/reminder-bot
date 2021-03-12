"""Reminder Bot"""
from discord.ext import commands
import yaml

import utils


# Grabs the bot token
with open("token.txt", "r") as token_file:
    TOKEN = token_file.read()


# Starts the client
prefix = utils.get_prefix()
prefix_func = commands.when_mentioned_or("{} ".format(prefix), prefix)
REMINDER_BOT = commands.Bot(command_prefix=prefix_func)


@REMINDER_BOT.event
async def on_ready():
    """Responds to when the bot readys"""
    # Setup the collections and reminders, print a status message

    with open("extensions.yml", "r") as extensions_file:
        extensions_file = yaml.load(extensions_file, Loader=yaml.Loader)
        for cog in extensions_file:
            REMINDER_BOT.load_extension(cog)
            print(f"Loaded cog {cog}")
    print(f"{REMINDER_BOT.user} connected to discord : )")


# Runs the client
REMINDER_BOT.run(TOKEN)
