import discord
from discord.ext import commands

from typing import Optional

import cogs.checks
import database
import utils


class SearchReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["search", "search_r", "sr"])
    async def search_reminders(self, ctx, date: Optional[str] = None):
        """Searches for reminders on a specific day"""
        if date:
            try:
                date = utils.split_date(date)
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
        await ctx.send(
            embed=utils.generate_embed("Search Results:", f"```{message}```")
        )

    @search_reminders.error
    async def search_reminders_error(self, ctx, error):
        await ctx.send(
            embed=utils.generate_embed(
                "Error",
                f"Something went wrong, try running {prefix}help search_reminders",
            )
        )


def setup(bot):
    bot.add_cog(SearchReminder(bot))
