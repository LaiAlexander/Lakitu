import discord
from discord.ext import commands


class TestCommit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)
    
    @commands.command(name="testcommit")
    async def test_commit(self, ctx):
        await ctx.send("This is from test_commit.py")


def setup(bot):
    bot.add_cog(TestCommit(bot))
