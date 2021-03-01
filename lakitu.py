import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setup
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix="!", intents=INTENTS)

# Load extensions
COGS = [file.stem for file in Path.cwd().joinpath("cogs").glob("**/*.py")]
for cog in COGS:
    BOT.load_extension(f"cogs.{cog}")


@BOT.event
async def on_ready():
    print(f"{BOT.user} is connected to the following guild(s):", flush=True)
    for guild in BOT.guilds:
        print(f"{guild.name}: (id: {guild.id})", flush=True)
    print("-----", flush=True)
    activity = discord.Activity(type=discord.ActivityType.watching, name="MK8D racers!")
    await BOT.change_presence(activity=activity)


if __name__ == "__main__":
    BOT.run(TOKEN)
