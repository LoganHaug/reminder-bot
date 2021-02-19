import discord
from discord.ext import commands

import utils

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['p'])
    async def ping(self, ctx):
        await ctx.send(embed=utils.generate_embed("Pong", f"{self.bot.latency * 1000:2.3f} ms"))
    
    @commands.command(aliases=["g"])
    async def graph(self, ctx):
        """Sends the graph"""
        file = discord.File("image.svg", filename="da_graph.svg")
        await ctx.send("", file=file)

def setup(bot):
    bot.add_cog(Misc(bot))