from datetime import datetime
from typing import Optional

from discord.ext import commands

import database
import utils

prefix = utils.get_prefix()


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["search", "search_r", "sr", "s"])
    async def search_reminders(self, ctx, date: Optional[str] = None):
        """Searches for reminders on a specific day"""
        if date:
            try:
                date = utils.split_date(date)
                date = datetime(date["year"], date["month"], date["day"]).timestamp()
            except UnboundLocalError:
                await ctx.reply(
                    embed=utils.generate_embed(
                        "", "Date was not in the correct format."
                    )
                )
                return 1
            db_search = database.get_reminders(
                ctx.message.guild.id,
                **{"date": date},
            )
        else:
            db_search = database.get_reminders(ctx.message.guild.id)
        message = ""
        for reminder in db_search:
            d = datetime.fromtimestamp((reminder["date"])).strftime("%Y-%m-%d %H:%M:%S")
            message += f'\n{reminder["reminder_id"]}\t{d}\t{reminder["reminder_text"]}\n'
        if not message:
            message = "No reminders found"
        await ctx.reply(
            embed=utils.generate_embed("Search Results:", f"```{message}```")
        )

    @search_reminders.error
    async def search_reminders_error(self, ctx, error):
        import traceback
        import sys
        traceback.print_exc(file=sys.stdout())
        print(error)
        print(type(error))
        
        await ctx.reply(
            embed=utils.generate_embed(
                "Error",
                f"Something went wrong, try running {prefix}help search_reminders",
            )
        )


async def setup(bot):
    await bot.add_cog(Search(bot))
