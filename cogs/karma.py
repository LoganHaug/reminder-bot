import discord
from discord.ext import commands
from pymongo import DESCENDING

import database

from typing import Optional

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_raw_reaction_add')
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # Upvote
        if payload.emoji.name == "👎":
            database.award_karma(message.guild.name, message.author.id, -1)
        # Downvote
        elif payload.emoji.name == "👍":
            database.award_karma(message.guild.name, message.author.id, 1)

    @commands.command(aliases=["lt", "l_t", "thumbers"])
    async def list_thumbers(self, ctx, user: Optional[str]) -> None:
        karma = database.DB[f"{ctx.message.guild.name}_USERS"].find().sort("karma", DESCENDING).limit(5)
        message = "User\t\t# of Thumbers"
        for user in karma:
            if "karma" in user.keys():
                message += f'\n{self.bot.get_user(user["_id"])}\t{user["karma"]}'
        await ctx.send(message)
 
def setup(bot):
    bot.add_cog(Karma(bot))