from discord.ext import commands

import cogs.checks as checks
import database
import utils


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.is_administrator)
    async def add_operator(self, ctx, user):
        """Adds an operator to the database"""
        database.insert_operator(ctx.message.guild.id, int(user[3:-1]))
        await ctx.reply(
            embed=utils.generate_embed(
                "Success, Operator added", f"Added user {user[3:-1]} as an operator"
            )
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
