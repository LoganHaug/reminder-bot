"""Reminder Bot"""
import discord
from discord.ext import commands
import pymongo
import yaml

import asyncio
import datetime
import threading
import time
from typing import Union, Optional

import database
from utils import generate_embed, is_administrator, split_date, split_time


# Grabs the bot token
with open("token.txt", "r") as token_file:
    TOKEN = token_file.read()

# Loads the repeating interval dictionary
with open("conversions.yml", "r") as conversion_file:
    conversion_dict = yaml.load(conversion_file, Loader=yaml.Loader)


# Holds reminders that are scheduled
scheduled_reminders = []

# Starts the client
prefix = ">"
prefix_func = commands.when_mentioned_or("{} ".format(prefix), prefix)
REMINDER_BOT = commands.Bot(command_prefix=prefix_func)


def is_operator(ctx):
    """Returns whether the user of the context is an operator of the bot"""
    return bool(
        database.DB[f"{ctx.message.guild}_USERS"].find_one(
            {"_id": ctx.message.author.id}
        )
    )



@REMINDER_BOT.command()
@commands.check(is_administrator)
async def add_operator(ctx, user):
    database.insert_operator(ctx.message.guild, int(user[3:-1]))
    await ctx.send(
        embed=generate_embed(
            "Success, Operator added", f"Added user {user[3:-1]} as an operator"
        )
    )


async def remind(reminder: dict):
    """Execute one reminder"""
    # Check if the reminder is in the future
    if reminder["date"] - time.time() > 0:
        # Get the channel object to send the message
        channel = REMINDER_BOT.get_channel(reminder["channel"])
        # Wait until the reminder should go off
        await asyncio.sleep(reminder["date"] - time.time())
        # Checks if the reminder is still scheduled, in case of deletion
        if reminder in scheduled_reminders:
            # Send the reminder text in the channel
            await channel.send(f"Reminder:\n{reminder['reminder_text']}")
            # Remove the reminder
            database.remove_reminder(reminder)
    # Schedules a repeating reminder
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

    reminders = database.get_reminders()
    new_schedule = []
    for scheduled_reminder in scheduled_reminders:
        if scheduled_reminder in reminders:
            new_schedule.append(scheduled_reminder)
    scheduled_reminders.clear()
    scheduled_reminders.extend(new_schedule)
    # Stores all the reminder tasks
    tasks = []
    # Create tasks for all reminders, call the remind function
    for reminder in reminders:
        # If the current reminder is not scheduled, schedule it
        if reminder not in scheduled_reminders:
            scheduled_reminders.append(reminder)
            tasks.append(asyncio.create_task(remind(reminder)))
    # Run the tasks
    asyncio.gather(*tasks)


@REMINDER_BOT.command(
    help="Date should be in month/day/year format, either with slashes or dashes (ex. month/day/year or month-day-year\n\nRepeating is an interval of time after which the reminder should be sent again, must be either daily, weekly, biweekly, or triweekly\n\nText is the text the reminder will be sent with, wrap with quotations if this contains whitespace"
)
@commands.check(is_operator)
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
        _date = split_date(date)
        _time = split_time(time)
    except UnboundLocalError:
        raise commands.UserInputError("Date or time was not in the correct format.")
    if repeating and repeating not in conversion_dict:
        raise commands.UserInputError()
    # Tries to insert the reminder
    result = database.insert_reminder(
        ctx.guild.name,
        ctx.channel.id,
        _date["year"],
        _date["month"],
        _date["day"],
        _time["hour"],
        _time["minute"],
        text,
        repeating,
    )
    # Sends a status message, and restarts the reminders
    if result:
        # TODO: confirm reminders with reactions
        asyncio.create_task(setup_reminders())
        await ctx.send(
            embed=generate_embed(
                "Reminder Stored", f"{date}\n{time}\n{text}\nrepeating: {repeating}"
            )
        )
    # This means the insertion of the reminder failed
    else:
        await ctx.send(
            embed=generate_embed(
                "Error",
                "`This reminder already exists in the database or is not in the future`",
            )
        )


@add_reminder.error
async def add_reminder_error(ctx, error):
    """Called when add_reminder() errors"""
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(
            embed=generate_embed("Error", f"`{error} Run {prefix}help add_reminder`")
        )
    elif isinstance(error, commands.errors.UserInputError):
        await ctx.send(
            embed=generate_embed("Error", f"`{error} Run {prefix}help add_reminder`")
        )
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            embed=generate_embed(
                "Error", "`You do not have permissions for this command`"
            )
        )
    else:
        await ctx.send(
            embed=generate_embed(
                "Error",
                f"`An unexpected error has occured, run {prefix}help add_reminder`",
            )
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
            ctx.message.guild,
            **{"year": date["year"], "month": date["month"], "day": date["day"]},
        )
    else:
        db_search = database.get_reminders(ctx.message.guild)
    message = ""
    for reminder in db_search:
        message += f'\n{reminder["_id"]}\t{reminder["human_readable_time"]}\t{reminder["reminder_text"]}\n'
    if not message:
        message = "No reminders found"
    await ctx.send(embed=generate_embed("Search Results:", f"```{message}```"))


@search_reminders.error
async def search_reminders_error(ctx, error):
    await ctx.send(
        embed=generate_embed(
            "Error", f"Something went wrong, try running {prefix}help search_reminders"
        )
    )


# TODO: update command


@REMINDER_BOT.command()
@commands.check(is_operator)
async def delete_reminder(ctx, index: int):
    """Deletes a reminder at a specific index"""
    search_result = database.get_reminders(ctx.message.guild, **{"_id": index})
    if search_result != []:
        delete_result = database.remove_reminder(search_result[0])
        if delete_result:
            await ctx.send(
                embed=generate_embed(
                    "Deleted Reminder", "The reminder was successfully removed"
                )
            )
        else:
            await ctx.send(embed=generate_embed("Error", "Something went wrong"))
    else:
        await ctx.send(
            embed=generate_embed("Error", "Could not find a reminder at this index")
        )



@delete_reminder.error
async def delete_reminders_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            embed=generate_embed(
                "Error", "`You do not have permissions for this command`"
            )
        )
    else:
        await ctx.send(
            embed=generate_embed(
                "Error", f"{error} Try running {prefix}help delete_reminder"
            )
        )


@REMINDER_BOT.event
async def on_ready():
    """Responds to when the bot readys"""
    # Setup the collections and reminders, print a status message
    asyncio.create_task(setup_reminders())
    print(f"{REMINDER_BOT.user} connected to discord : )")


# Runs the client
REMINDER_BOT.run(TOKEN)
