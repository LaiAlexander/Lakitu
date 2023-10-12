# Lakitu
A Discord bot to keep track of time trial leaderboards in Mario Kart 8 Deluxe.\
[![Tests](https://github.com/LaiAlexander/Lakitu/actions/workflows/tests.yml/badge.svg)](https://github.com/LaiAlexander/Lakitu/actions/workflows/tests.yml)
[![Build](https://github.com/LaiAlexander/Lakitu/actions/workflows/build.yml/badge.svg)](https://github.com/LaiAlexander/Lakitu/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/LaiAlexander/Lakitu/badge.svg?branch=main)](https://coveralls.io/github/LaiAlexander/Lakitu?branch=main)
![GitHub](https://img.shields.io/github/license/LaiAlexander/Lakitu)

### Milestone progress
[![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/LaiAlexander/Lakitu/1)](https://github.com/LaiAlexander/Lakitu/milestone/1)
[![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/LaiAlexander/Lakitu/2)](https://github.com/LaiAlexander/Lakitu/milestone/2)
[![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/LaiAlexander/Lakitu/3)](https://github.com/LaiAlexander/Lakitu/milestone/3)
[![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/LaiAlexander/Lakitu/4)](https://github.com/LaiAlexander/Lakitu/milestone/4)

## Overview
Lakitu is a self hosted Discord bot to keep track of various Mario Kart 8 Deluxe stats. It's meant to make competition fun in your friend group. Lakitu can keep track of time trial records, both for individual tracks, cups and speed run categories. Currently only 150cc and 200cc is supported. Lakitu can also keep track of the versus ratings of players.

## Setup
0. Clone/fork this repo.
1. Create a Discord application and bot user. [Real Python](https://realpython.com/how-to-make-a-discord-bot-python/#creating-an-application) has a good guide ready. The bot user only needs the `Send Messages` permission. You can name the app/bot whatever you like and give it a custom profile picture.
2. Add the bot you made in step two to your server. Again, check [Real Python's guide](https://realpython.com/how-to-make-a-discord-bot-python/#adding-a-bot-to-a-guild)
3. The bot needs both `Presence Intent` and `Server Members Intent` to function. This may be changed at a later point. Check those boxes in the bot tab of your Discord application.
4. Copy the bot token from the bot tab of your Discord application. Do not share your token with anyone! In the root directory of the bot, you must make a file calle `.env`. The content of `.env` should be just one line, like this:
`DISCORD_TOKEN=your-token-here`
Remember to replace `your-token-here` with your actual bot token.
5. Run `generate_json.py`. 
6. Not strictly necesseary, but it's heavily recommended to make and run the bot from a virtual environment. If you don't want to use a virtual environment, skip to step 8.
Create a virtual environment in the project folder with `python -m venv env`. `env` will be your name for the virtual environment. 
7. Activate the virtual environment. 
Windows: `. env/Scripts/activate`
Unix: `. env/bin/activate`
8. Install requirements. This is easiest to do with pip. `pip install -r requirements.txt`
9. Run the bot! `python lakitu.py`


## Requirements
* [`discord.py==1.6.0`](https://github.com/Rapptz/discord.py)
* [`GitPython==3.1.14`](https://github.com/gitpython-developers/GitPython)
* [`python-dotenv==0.15.0`](https://github.com/theskumar/python-dotenv)

You can install all of the above at once with `pip install -r requirements.txt`

Also requires at least [Python 3.7](https://www.python.org/downloads/).

## Usage
* View all the different commands: `!help`
* View help text of a specific commands: `!help [command] [subcommand]`\
[subcommand] is optional
* Register your time trial result: `!timetrial [track name/alias/cup/category] [HH:MM:SS.ms]/[MM:SS.ms] [cc]`
* Delete your time trial result: `!timetrial delete [track name/alias/cup/category] [cc]`
* View info about a track/cup/category: `!timetrial info [track name/cup/category]`
* Get a count of your records: `!timetrial myrecords`
* View all of your records: `!timetrial myrecords list`
* View the VR of a player: `!vr [name]`\
If [name] is `me` or blank, it will show your VR.
* Register/update your VR:
`!vr update [your vr]`

### For developers
These commands are only usable by the owner of the bot, i.e. the Discord account that made the Discord application/bot during setup.
* Unload a cog: `!unload [cog]`
* Load a cog: `!load [cog]`
* Reload a cog: `!reload [cog]`\
If [cog] is blank, it will unload, load or reload all cogs. `cog_manager` will never be unloaded. `cog_manager` makes it possible to test new code for the bot without constantly having to restart the bot. Very useful when developing new features.
* Update the bot: `!update`\
This will attempt to pull the newest updates from GitHub, and then reload all cogs. This makes it possible to update the bot remotely while it's running. It's currently only possible to load/reload new cogs, so if there's changes to the core `lakitu.py`, the bot still has to be restarted manually.

## Running tests
First, navigate/cd to the root directory of the project. Test coverage is lackluster at the moment, but is under active improvement. Verbose mode (-v) is optional.
Run all tests with either unittest or pytest.\
unittest: `python -m unittest discover -b (-v)`\
pytest: `pytest (-v)`

## License
[MIT](https://choosealicense.com/licenses/mit/)
