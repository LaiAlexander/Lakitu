from pathlib import Path

import discord
from discord.ext import commands


class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)

    @commands.command(name="owner", help="Check if you are owner of this bot.")
    async def owner(self, ctx):
        owner = self.bot.is_owner(ctx.author)
        owner = "Yes" if owner else "No"
        await ctx.send(f"Are you the owner of me? {owner}")

    @commands.command(name="reload", help="Reload a cog")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog=None):
        if cog:
            async with ctx.typing():
                embed = discord.Embed(title=f"Reloading {cog}")
                try:
                    self.bot.reload_extension(f"cogs.{cog}")
                    embed.add_field(
                        name=f"Reloaded {cog}!", value="Success!", inline=False
                    )
                    print(f"{cog} cog has been reloaded\n-----", flush=True)
                except Exception as e:
                    embed.add_field(
                        name=f"Failed to reload {cog}.", value=e, inline=False
                    )
                    print(f"Execption: {e}", flush=True)
        else:
            async with ctx.typing():
                embed = discord.Embed(title="Reloading all cogs")
                cogs = [
                    file.stem for file in Path.cwd().joinpath("cogs").glob("**/*.py")
                ]
                for cog in cogs:
                    try:
                        self.bot.reload_extension(f"cogs.{cog}")
                        embed.add_field(
                            name=f"Reloaded {cog}!", value="Success!", inline=False
                        )
                        print(f"{cog} cog has been reloaded\n-----", flush=True)
                    except Exception as e:
                        embed.add_field(
                            name=f"Failed to reload {cog}.", value=e, inline=False
                        )
                        print(f"Execption: {e}", flush=True)
        await ctx.send(embed=embed)

    @commands.command(name="load", help="Load a new cog")
    @commands.is_owner()
    async def load_cog(self, ctx, cog=None):
        if cog:
            async with ctx.typing():
                embed = discord.Embed(title=f"Loading {cog}")
                try:
                    self.bot.load_extension(f"cogs.{cog}")
                    embed.add_field(
                        name=f"Loaded {cog}!", value="Success!", inline=False
                    )
                    print(f"{cog} cog has been loaded\n-----", flush=True)
                except Exception as e:
                    embed.add_field(
                        name=f"Failed to load {cog}.", value=e, inline=False
                    )
                    print(f"Execption: {e}", flush=True)
        else:
            async with ctx.typing():
                embed = discord.Embed(title="Loading all cogs")
                cogs = [
                    file.stem for file in Path.cwd().joinpath("cogs").glob("**/*.py")
                ]
                for cog in cogs:
                    try:
                        self.bot.load_extension(f"cogs.{cog}")
                        embed.add_field(
                            name=f"Loaded {cog}!", value="Success!", inline=False
                        )
                        print(f"{cog} cog has been loaded\n-----", flush=True)
                    except Exception as e:
                        embed.add_field(
                            name=f"Failed to load {cog}.", value=e, inline=False
                        )
                        print(f"Execption: {e}", flush=True)
        await ctx.send(embed=embed)

    @commands.command(name="unload", help="Unload a cog")
    @commands.is_owner()
    async def unload_cog(self, ctx, cog=None):
        this_cog = "cog_manager"
        if cog == this_cog:
            print(f"Don't ever unload {cog}", flush=True)
            embed = discord.Embed(title=f"Unloading {cog}")
            embed.add_field(
                name=f"Not allowed to unload {cog}", value="Denied", inline=False
            )
            await ctx.send(embed=embed)
            return
        if cog:
            async with ctx.typing():
                embed = discord.Embed(title=f"Unloading {cog}")
                try:
                    self.bot.unload_extension(f"cogs.{cog}")
                    embed.add_field(
                        name=f"Unloaded {cog}!", value="Success!", inline=False
                    )
                    print(f"{cog} cog has been unloaded\n-----", flush=True)
                except Exception as e:
                    embed.add_field(
                        name=f"Failed to unload {cog}.", value=e, inline=False
                    )
                    print(f"Execption: {e}", flush=True)
        else:
            async with ctx.typing():
                embed = discord.Embed(title="Unloading all cogs")
                cogs = [
                    file.stem for file in Path.cwd().joinpath("cogs").glob("**/*.py")
                ]
                for cog in cogs:
                    if cog == this_cog:
                        embed.add_field(
                            name=f"Not allowed to unload {cog}",
                            value="Denied",
                            inline=False,
                        )
                        print(f"Don't ever unload {cog}", flush=True)
                        continue
                    try:
                        self.bot.unload_extension(f"cogs.{cog}")
                        embed.add_field(
                            name=f"Unloaded {cog}!", value="Success!", inline=False
                        )
                        print(f"{cog} cog has been unloaded\n-----", flush=True)
                    except Exception as e:
                        embed.add_field(
                            name=f"Failed to unload {cog}.", value=e, inline=False
                        )
                        print(f"Execption: {e}", flush=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CogManager(bot))
