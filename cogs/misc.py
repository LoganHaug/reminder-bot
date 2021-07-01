import discord
from discord.ext import commands
from PIL import Image

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
        await ctx.send(
            "", file=discord.File("img/image.svg", filename="img/da_graph.svg")
        )

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

    @commands.command(aliases=["gr", "g_radia"])
    async def gen_radia(self, ctx, date):
        """Generates the World of Radia given a date

        Enter a date with format Month-Day-Year or Month/Day/Year
        ex. June 1st 2000 -> 06/01/2000 or 06-01-2000"""
        date = utils.split_date(date)

        if date is None:
            ctx.send(embed=utils.generate_embed("Error", "Please enter a valid date"))
        center = Image.open("img/background.png")

        ringsFiles = [
            "img/rings/ring6.png",
            "img/rings/ring5.png",
            "img/rings/ring4.png",
            "img/rings/ring3.png",
            "img/rings/ring2.png",
            "img/rings/ring1.png",
            "img/rings/ring0.png",
        ]
        ringSpeeds = [0.25, 1, -2, 1.5, 1, -2, 0]  # num rotations per year

        dayOfYear = 360 * date["year"] + 30 * (date["month"] - 1) + date["day"] - 1

        for ring in ringsFiles:
            temp = Image.open(ring)
            temp = temp.rotate(
                angle=-ringSpeeds[ringsFiles.index(ring)] * 0.6 * dayOfYear
            )  # 360 days per year
            center.paste(temp, (0, 0), temp)
        center.save("img/out.png")
        await ctx.send(file=discord.File("img/out.png", filename="img/out.png"))


def setup(bot):
    bot.add_cog(Misc(bot))
