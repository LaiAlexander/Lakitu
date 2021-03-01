import discord
from discord.ext import commands

import git


class Updater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)

    @commands.command(name="gitpull", help="Pull updates from github.", hidden=True)
    @commands.is_owner()
    async def git_pull(self, ctx):
        status = git.cmd.Git().pull()
        print(f"Pulling from Github...\n{status}")
        embed = discord.Embed(title="Pulling from Github")
        embed.add_field(name="Status:", value=status)
        await ctx.send(embed=embed)

    @commands.command(name="update", help="Update bot", hidden=True)
    @commands.is_owner()
    async def update(self, ctx):
        cog_manager = self.bot.get_cog("CogManager")
        await self.git_pull(ctx)
        await cog_manager.unload_cog(ctx)
        await cog_manager.load_cog(ctx)
        embed = discord.Embed(title="Update successful", description="The bot has been updated!")
        print("Update successful!", flush=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Updater(bot))
