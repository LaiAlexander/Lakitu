import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

# import leaderboard

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD_TOKEN")

INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix="!", intents=INTENTS)
# Load extensions
COGS = [file.stem for file in Path.cwd().joinpath("cogs").glob("**/*.py")]
for cog in COGS:
    BOT.load_extension(f"cogs.{cog}")

@BOT.event
async def on_ready():
    guild = discord.utils.get(BOT.guilds, name=GUILD)
    print(
        f'{BOT.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n-----'
    , flush=True)
    activity = discord.Activity(type=discord.ActivityType.watching, name="MK8D racers!")
    await BOT.change_presence(activity=activity)

BOT.run(TOKEN)
