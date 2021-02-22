import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import leaderboard

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD_TOKEN")

INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix="!", intents=INTENTS)
BOT.add_cog(leaderboard.Leaderboard(BOT))

@BOT.event
async def on_ready():
    guild = discord.utils.get(BOT.guilds, name=GUILD)
    print(
        f'{BOT.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    , flush=True)

BOT.run(TOKEN)
