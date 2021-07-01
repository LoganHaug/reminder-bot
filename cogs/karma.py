import discord
from discord.ext import commands
from pymongo import DESCENDING

import database
import utils

from typing import Optional


class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # Upvote
        if payload.emoji.name == "👎":
            database.award_karma(message, -1)
        # Downvote
        elif payload.emoji.name == "👍":
            database.award_karma(message, 1)

    @commands.command(aliases=["lt", "l_t", "thumbers"])
    async def list_thumbers(self, ctx, user: Optional[str]) -> None:
        """Lists the number of thumbers for a user or the top 5 on the server"""
        if user and len(ctx.message.mentions) >= 1:
            user = database.DB[str(ctx.message.guild.id)].find_one(
                {"_id": ctx.message.mentions[-1].id}
            )
            if user and "karma" in user.keys():
                await ctx.send(
                    embed=utils.generate_embed(
                        f"{user['name']} has {user['karma']} thumbers", ""
                    )
                )
            else:
                await ctx.send(
                    embed=utils.generate_embed(
                        f"{ctx.message.mentions[-1].name} has no thumbers", ""
                    )
                )
        else:
            karma = (
                database.DB[str(ctx.message.guild.id)]
                .find()
                .sort("karma", DESCENDING)
                .limit(5)
            )
            message = ""
            for user in karma:
                if "karma" in user.keys():
                    message += f'\n{user["karma"]} {user["name"]}'
            await ctx.send(embed=utils.generate_embed("# of Thumbers   User", message))


def setup(bot):
    bot.add_cog(Karma(bot))
