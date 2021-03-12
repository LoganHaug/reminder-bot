import discord
from discord.ext import commands

from cogs.checks import is_operator
import database
import utils


class DeleteReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["delete", "delete_r", "dr"])
    @commands.check(is_operator)
    async def delete_reminder(self, ctx, index: int):
        """Deletes a reminder at a specific index"""
        search_result = database.get_reminders(ctx.message.guild, **{"_id": index})
        if search_result != []:
            delete_result = database.remove_reminder(search_result[0])
            if delete_result:
                await ctx.send(
                    embed=utils.generate_embed(
                        "Deleted Reminder", "The reminder was successfully removed"
                    )
                )
            else:
                await ctx.send(embed=utils.generate_embed("Error", "Something went wrong"))
        else:
            await ctx.send(
                embed=utils.generate_embed(
                    "Error", "Could not find a reminder at this index"
                )
            )


    @delete_reminder.error
    async def delete_reminders_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send(
                embed=utils.generate_embed(
                    "Error", "`You do not have permissions for this command`"
                )
            )
        else:
            await ctx.send(
                embed=utils.generate_embed(
                    "Error", f"{error} Try running {prefix}help delete_reminder"
                )
            )

def setup(bot):
    bot.add_cog(DeleteReminder(bot))