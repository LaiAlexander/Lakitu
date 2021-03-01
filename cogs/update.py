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
        async with ctx.typing():
            with open("requirements.txt", "r") as req:
                req_list = [line.strip() for line in req.readlines()]
            status = git.cmd.Git().pull()
            print(f"Pulling from Github...\n{status}")
            with open("requirements.txt", "r") as req:
                new_req_list = [line.strip() for line in req.readlines()]
            modules_to_install = [module for module in new_req_list if module not in req_list]
            embed = discord.Embed(title="Pulling from Github")
            embed.add_field(name="Status:", value=status)  
            if modules_to_install:
                print("Installing requirements...", flush=True)
                print(modules_to_install, flush=True)
                for module in modules_to_install:
                    print("Installing " + module, flush=True)
                    status = pip_install(module)
                    embed.add_field(name=module, value=status)
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

    @commands.command(name="installreqs", help="Install requirements", hidden=True)
    @commands.is_owner()
    async def install_all_requirements(self, ctx):
        async with ctx.typing():
            embed = discord.Embed(title="Installing all requirements...")
            await ctx.send(embed=embed)
            status = pip_install("requirements.txt")
            embed = discord.Embed(title="Status", description=status)
            await ctx.send(embed=embed)


def pip_install(module):
    # Unsure if it's "pip" or "pip3" on macOS
    if sys.platform == "linux" or sys.platform == "darwin":
        pip = "pip3"
    else:
        pip = "pip"
    print("In pip_install", flush=True)
    if module == "requirements.txt":
        args = [sys.executable, "-m", pip, "install", "-r", module]
    else:
        args = [sys.executable, "-m", pip, "install", module]
    try:
        result = subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True # This line requires at least Python 3.7
        )
    except subprocess.CalledProcessError as exc:
        print("Exception occured:", flush=True)
        print(exc, flush=True)
        return str(exc)
    print(result.stdout, flush=True)
    print(args, flush=True)
    status = "Requirements successfully installed!\n-----\n" + result.stdout
    if len(status) > 1500:
        truncated = status[1500:]
        status = status[:1500]
        status = status + f"\n-----\nRest of message ({len(truncated)} characters) truncated."
    return status


def setup(bot):
    bot.add_cog(Updater(bot))
