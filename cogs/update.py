import subprocess
import sys

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
        with open("requirements.txt", "r") as req:
            req_list = [line.strip() for line in req.readlines()]
        print(f"Pulling from Github...\n{status}")
        with open("requirements.txt", "r") as req:
            new_req_list = [line.strip() for line in req.readlines()]
        modules_to_install = [module for module in new_req_list if module not in req_list]
        embed = discord.Embed(title="Pulling from Github")
        embed.add_field(name="Status:", value=status)
        print("Installing requirements...", flush=True)
        for module in modules_to_install:
            pip_install(module)
        await ctx.send(embed=embed)

    @commands.command(name="update", help="Update bot", hidden=True)
    @commands.is_owner()
    async def update(self, ctx):
        cog_manager = self.bot.get_cog("CogManager")
        await self.git_pull(ctx)
        await cog_manager.unload_cog(ctx)
        await cog_manager.load_cog(ctx)
        embed = discord.Embed(
            title="Update successful", description="The bot has been updated!"
        )
        print("Update successful!", flush=True)
        await ctx.send(embed=embed)


def pip_install(module):
    subprocess.check_call(
        [sys.executable, "-m", "pip3", "install", "-r", module]
    )


def setup(bot):
    bot.add_cog(Updater(bot))
