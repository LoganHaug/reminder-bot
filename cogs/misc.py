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

    @commands.command(aliases=["g"])
    async def graph(self, ctx):
        """Sends the graph"""
        utils.generate_graph()
        file = discord.File("image.svg", filename="da_graph.svg")
        await ctx.send("", file=file)

    @commands.command(aliases=["pet"])
    async def pat(self, ctx):
        """Pats the reminder bot, or a user"""
        if len(ctx.message.mentions) >= 1:
            pats = database.increment_pat(ctx.guild.id, ctx.message.mentions[-1].id)
            user = ctx.message.mentions[-1].name
        else:
            pats = database.increment_pat(ctx.guild.id, self.bot.user.id)
            user = self.bot.user.name
        if pats == 1:
            await ctx.send(
                embed=utils.generate_embed("💜", f"{user} has received {pats} pat")
            )
        else:
            await ctx.send(
                embed=utils.generate_embed("💜", f"{user} has received {pats} pats")
            )


def setup(bot):
    bot.add_cog(Misc(bot))
