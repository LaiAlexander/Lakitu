import discord
from discord.ext import commands


class Elo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)


def setup(bot):
    bot.add_cog(Elo(bot))
