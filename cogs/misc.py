import discord
from discord.ext import commands

import database
import utils


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["p"])
    async def ping(self, ctx):
        await ctx.send(
            embed=utils.generate_embed("Pong", f"{self.bot.latency * 1000:2.3f} ms")
        )


def setup(bot):
    bot.add_cog(Misc(bot))
