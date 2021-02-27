import datetime
import json
from pathlib import Path

import discord
from discord.ext import commands

with open(Path.cwd().joinpath("data", "tracks.json"), "r") as read_file:
    TRACKS = json.load(read_file)

with open(Path.cwd().joinpath("data", "aliases.json"), "r") as read_file:
    ALIASES = json.load(read_file)

with open(Path.cwd().joinpath("data", "cups.json"), "r") as read_file:
    CUPS = json.load(read_file)

with open(Path.cwd().joinpath("data", "speed_run_categories.json"), "r") as read_file:
    SPEED_RUN_CATEGORIES = json.load(read_file)

with open(Path.cwd().joinpath("data", "versus_rating.json"), "r") as read_file:
    VERSUS_RATINGS = json.load(read_file)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)
    
    @commands.group(name="vr", invoke_without_command=True, help="View the VR of a player. Name is the name of the player to search for, but name may also be 'me' for yourself or 'all' to view all players. You may also add 'all' at the end to view the complete list.")
    async def vrating(self, ctx, name=None, view_all=None):
        # if ctx.invoked_subcommand is None:
        discord_id = None
        if not name or name == "all" or name == "me":
            discord_id = ctx.author.id
        view_all = view_all == "all" or name == "all"

        for vr in VERSUS_RATINGS["vrs"]:
            if vr["Name"].lower() == str(name).lower():
                discord_id = vr["ID"]

        user = self.bot.get_user(discord_id)
        if not user:
            await ctx.send(f"Could not find {name} on the vr leaderboard.")
            return

        standing, leaderboard_title, leaderboard = view_versus_rating(discord_id, all_places=view_all)

        status = ""
        leaderboard = {"name": leaderboard_title, "value": leaderboard}
        embed = make_embed("Versus ratings", status, standing, user.name, user.avatar_url, leaderboard)
        await ctx.send(embed=embed)

    @vrating.command(name="update", help="Update your VR.")
    async def update(self, ctx, vr):
        name = ctx.author.name
        discord_id = ctx.author.id
        status, standing, leaderboard_title, leaderboard = update_versus_rating(name, discord_id, vr)
        leaderboard = {"name": leaderboard_title, "value": leaderboard}
        embed = make_embed("Versus ratings", status, standing, name, ctx.author.avatar_url, leaderboard)
        await ctx.send(embed=embed)

    @commands.group(name="timetrial", aliases=["tt", "speedrun", "sr"], invoke_without_command=True, help="Register a new time trial record, view your records or view the records of a course.")
    async def timetrial(self, ctx, race, time, cc):
        # TODO should probaly make a Record here and pass it to add_record. Easier to tell the user what went wrong this wai, if anything.
        race_data = get_race_name(race)
        if not race_data:
            await ctx.send(f"Sorry, could not find a track named {race}. Remember capital letters and put the name within quotation marks if it is a multi-word name.")
            return
        name = ctx.author.name
        discord_id = ctx.author.id
        race_name = race_data["name"]
        race_info, status, standing, leaderboard_title, leaderboards, category_name = add_record(race_data, name, discord_id, time, cc)
        status = race_info + "\n" + status
        field_150 = {"name": leaderboard_title + "(150cc):", "value": leaderboards["150cc"]}
        field_200 = {"name": leaderboard_title + "(200cc):", "value": leaderboards["200cc"]}
        embed = make_embed(race_name, status, standing, name, ctx.author.avatar_url, field_150, field_200)
        file = None
        if category_name in ("tracks", "cups"):
            icon_url = Path.cwd().joinpath("assets", category_name, f"{race_name}.png")
            file = discord.File(icon_url, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(embed=embed, file=file)

    @timetrial.command(name="myrecords", help="Counts how many records you currently have. Do '!timetrial myrecords list' if you want to see the list of all your records.")
    async def my_records(self, ctx, list_records=None):
        name = ctx.author.name
        discord_id = ctx.author.id
        count_150, count_200 = count_personal_records(discord_id)
        standing = f"You have {count_150} records for 150cc and {count_200} records for 200cc."
        if not list_records:  
            embed = make_embed(f"{name}'s records", "", standing, name, ctx.author.avatar_url)
        elif list_records.lower() == "list":
           records = view_personal_records(discord_id)
           field_150 = {"name": "150cc", "value": "\n".join(records["150cc"])}
           field_200 = {"name": "200cc", "value": "\n".join(records["200cc"])}
           embed = make_embed(f"{name}'s records", "", standing, name, ctx.author.avatar_url, field_150, field_200)
        else:
            await ctx.send(f"{list_records} is not a valid command.")
            return
        await ctx.send(embed=embed)
    
    @timetrial.command(name="info", help="View the records of a particular course.")
    async def race_records(self, ctx, race_name, cc=None):
        # TODO Should just return both 150 and 200 cc records.
        # TODO Does not show anything if no records exists yet.
        race_data = get_race_name(race_name)
        if not race_data:
            await ctx.send(f"Sorry, could not find a track named {race_name}. Remember capital letters and put the name within quotation marks if it is a multi-word name.")
            return
        ccs = ["150", "200"]
        if cc not in ccs:
            await ctx.send(f"Sorry, {cc} is not a valid cc. Enter 150 or 200.")
            return
        race_info, standing, leaderboard_title, leaderboards = view_course_records(race_data["name"], race_data["category_data"], race_data["category_name"], cc, ctx.author.name)
        field_150 = {"name": leaderboard_title + "(150cc):", "value": leaderboards["150cc"]}
        field_200 = {"name": leaderboard_title + "(200cc):", "value": leaderboards["200cc"]}
        embed = make_embed(race_data["name"], race_info, standing, ctx.author.name, ctx.author.avatar_url, field_150, field_200)
        file = None
        if race_data["category_name"] in ("tracks", "cups"):
            icon_url = Path.cwd().joinpath("assets", race_data["category_name"], f"{race_data['name']}.png")
            file = discord.File(icon_url, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(embed=embed, file=file)


def make_embed(title, status, standing, name, icon_url, field_1=None, field_2=None):
    embed = discord.Embed()
    embed.color = discord.Color.blue()
    embed.title = title
    embed.description = status + "\n" + standing
    embed.set_author(name=name)
    if field_1:
        embed.add_field(name=field_1["name"], value=field_1["value"])
    if field_2:
        embed.add_field(name=field_2["name"], value=field_2["value"])
    if icon_url:
        embed.set_author(name=name, icon_url=icon_url)
        embed.set_thumbnail(url=icon_url)
    return embed

class Record():
    def __init__(self, name, discord_id, time):
        self.name = name
        self.discord_id = discord_id
        time = time.replace(".", ":")
        time = time.split(":")
        if len(time) == 3:
            time.insert(0, "0")
        # dont think the following is needed anymore, but will keep it for now.
        # if len(time[3]) < 3:
        #     if len(time[3]) < 2:
        #         time[3] = time[3] + "0"
        #     time[3] = time[3] + "0"
        self.time = datetime.datetime.strptime((":").join(time), "%H:%M:%S:%f").time()
        # should this be a time or a datetime object?

    def time_to_str(self):
        # Only want the three first digits of the microseconds, not all six
        if self.time.hour < 1:
            return self.time.strftime("%M:%S.%f")[:-3]
        return self.time.strftime("%H:%M:%S.%f")[:-3]

    def __lt__(self, value):
        return self.time < value.time

    def __le__(self, value):
        return self.time <= value.time

    def __eq__(self, value):
        return self.time == value.time and self.name == value.name

    def __str__(self):
        return self.name + ": " + self.time_to_str()

    def __repr__(self):
        return self.name + ": " + str(self.time)

    @classmethod
    def from_json(cls, record_dict):
        name = record_dict["Name"]
        discord_id = record_dict["ID"]
        time = record_dict["Time"]
        return cls(name, discord_id, time)

    @property
    def json(self):
        record = {}
        record["Name"] = self.name
        record["ID"] = self.discord_id
        record["Time"] = self.time_to_str()
        return record

class VersusRating():
    def __init__(self, name, discord_id, vr):
        # self.identifier = {"Name": name, "ID": discord_id}
        self.name = name
        self.discord_id = discord_id
        self.vr = int(vr)

    def __lt__(self, value):
        return self.vr < value.vr

    def __eq__(self, value):
        return self.vr == value.vr

    def __str__(self):
        return f"{self.name}: {self.vr}"

    @classmethod
    def from_json(cls, data):
        name = data["Name"]
        discord_id = data["ID"]
        vr = data["vr"]
        return cls(name, discord_id, vr)

    @property
    def json(self):
        v_rating = {}
        v_rating["Name"] = self.name
        v_rating["ID"] = self.discord_id
        v_rating["vr"] = self.vr
        return v_rating

def add_record(race_data=None, name=None, discord_id=None, time=None, cc=None):
    if not race_data and not name and not time:
        race_name, name, time, cc = [part.strip() for part in input("Shorthand for registering: (trackname/alias, name, time, cc):").split(",")]
    race_name = race_data["name"]
    category_name = race_data["category_name"]
    category = race_data["category_data"]
    if not race_name:
        return
    race = category[race_name]
    ccs = ["150", "200"]
    if cc not in ccs:
        print("Not valid cc")
        return
    cc = cc + "cc"

    # print("trying to make Record", flush=True)
    record = Record(name, discord_id, time)
    # print(record, flush=True)
    # print("Record made", flush=True)

    record_list = [Record.from_json(records) for records in race["Leaderboard"][cc]]
    for i, existing_record in enumerate(record_list):
        if record < existing_record:
            if record.name == existing_record.name:
                record_list[i] = record
                print("You beat your own record!")
                status = "You beat your own record!"
                break
            for old_record in record_list:
                if old_record.name == record.name:
                    print("This was identical")
                    record_list.remove(old_record)
                    break
            record_list.insert(i, record)
            print(existing_record.name + " have been beaten!")
            status = f"{existing_record.name} have been beaten!"
            break
        if record.name == existing_record.name:
            print("Your previous record is better!")
            status = "Your previous record is better!"
            break
    else:
        record_list.append(record)
        print("You have the record!")
        status = "You have the record!"
    record_list.sort()
    race["Leaderboard"][cc] = [record.json for record in record_list]
    race_info, standing, leaderboard_title, leaderboards = view_course_records(race_name, category, category_name, cc[:-2], name)
    with open(Path.cwd().joinpath("data", category_name + ".json"), "w") as outfile:
        json.dump(category, outfile, indent=4)

    # TODO consider returning a dict instead for these fucntions
    return race_info, status, standing, leaderboard_title, leaderboards, category_name

def get_race_name(name):
    result = {}  
    if ALIASES.get(name):
        name = ALIASES[name]
    if TRACKS.get(name):
        result["name"] = name
        result["category_name"] = "tracks"
        result["category_data"] = TRACKS
        return result
    name = name.title()
    if TRACKS.get(name):
        result["name"] = name
        result["category_name"] = "tracks"
        result["category_data"] = TRACKS
        return result
    if CUPS.get(name):
        result["name"] = name
        result["category_name"] = "cups"
        result["category_data"] = CUPS
        return result
    if SPEED_RUN_CATEGORIES.get(name):
        result["name"] = name
        result["category_name"] = "speed_run_categories"
        result["category_data"] = SPEED_RUN_CATEGORIES
        return result
    return None

def get_cc(cc):
    valid_cc = ["150", "200"]
    if cc not in valid_cc:
        print("Not valid cc.")
        return None
    return cc + "cc"

def view_course_records(race_name=None, category=None, category_name=None, cc=None, name=None):
    # TODO What happens when no records currently exist? Does not work as expected
    places_to_display = 5
    
    if not race_name or not category or not category_name or not cc:
        race_name, cc = [part.strip() for part in input("What track and cc? (trackname/alias, cc) ").split(",")]
        race_data = get_race_name(race_name)
        race_name = race_data["name"]
        category_name = race_data["category_name"]
        category = race_data["category_data"]
    if not name:
        name = input("What is your name? ")
    if not race_name:
        return

    race = category[race_name]

    cc = get_cc(cc)
    if not cc:
        return

    if category_name == "tracks":
        race_info = f"{race['Cup']} cup, {race['Course']} course.\nAlias: {race['Alias']}"
    elif category_name == "cups":
        race_info = f"{race['Course']} courses.\nTracks: {(', ').join(race['Tracks'])}"
    elif category_name == "speed_run_categories":
        race_info = f"Cups: {(', ').join(race['Cups'])}"

    record_list = race["Leaderboard"][cc]
    records = race["Leaderboard"]
    if not record_list:
        print("No records added yet!")
        return

    # record_list_150 = race["Leaderboard"]["150cc"]
    # record_list_200 = race["Leaderboard"]["200cc"]

    if len(record_list) < places_to_display:
        places_to_display = len(record_list)


    for i , record in enumerate(record_list):
        if record["Name"] == name:
            if i == 0:
                print(f"You are in {i + 1}. place!")
                standing = f"You are in {i + 1}. place!"
            else:
                print(f"You are in {i + 1}. place, behind {record_list[i - 1]['Name']}.")
                standing = f"You are in {i + 1}. place, behind {record_list[i - 1]['Name']}."
            break
    else:
        print("You are not on the leaderboard yet.")
        standing = "You are not on the leaderboard yet."

    print(f"Top {places_to_display} results:")
    leaderboard_title = f"Top {places_to_display} results "

    # leaderboard = []
    # i = 1
    # print(f"{i}. {Record.from_json(record_list[0])}")
    # leaderboard.append(f"{i}. {Record.from_json(record_list[0])}")
    # for j in range(1, places_to_display):
    #     if record_list[j - 1]["Time"] != record_list[j]["Time"]:
    #         i = j + 1
    #     print(f"{i}. {Record.from_json(record_list[j])}")
    #     leaderboard.append(f"{i}. {Record.from_json(record_list[j])}")
    # leaderboard = "\n".join(leaderboard)

    leaderboards = {}
    leaderboard_titles = {}

    print(records.items(), flush=True)
    for key, record_list in records.items():
        if len(record_list) < places_to_display:
            places_to_display = len(record_list)
        leaderboard_titles[key] = f"Top {places_to_display} results ({key})"
        # TODO the above might not work yet, change affected code and test it.
        # leaderboards[key] = []
        # leaderboards[key].append(f"{i}. {Record.from_json(record_list[0])}")
        leaderboard = []
        if not record_list:
            leaderboard.append(f"No records for {key} yet!")
        else:
            i = 1
            print(f"{i}. {Record.from_json(record_list[0])}")
            leaderboard.append(f"{i}. {Record.from_json(record_list[0])}")
            for j in range(1, places_to_display):
                if record_list[j - 1]["Time"] != record_list[j]["Time"]:
                    i = j + 1
                print(f"{i}. {Record.from_json(record_list[j])}")
                leaderboard.append(f"{i}. {Record.from_json(record_list[j])}")
        leaderboard = "\n".join(leaderboard)
        leaderboards[key] = leaderboard
    print(leaderboards, flush=True)

    return race_info, standing, leaderboard_title, leaderboards

def count_personal_records(discord_id = None):
    if not discord_id:
        discord_id = input("What discord_id? ")
    count_150 = 0
    count_200 = 0
    categories = [TRACKS, CUPS, SPEED_RUN_CATEGORIES]

    for category in categories:
        for race in category:
            leaderboard = category[race]["Leaderboard"]
            for cc, records in leaderboard.items():
                for record in records:
                    if record["ID"] == discord_id and cc == "150cc":
                        count_150 += 1
                    if record["ID"] == discord_id and cc == "200cc":
                        count_200 += 1
    return count_150, count_200

def view_personal_records(discord_id = None):
    ccs = {"150cc": False, "200cc": False}
    categories = [TRACKS, CUPS, SPEED_RUN_CATEGORIES]
    records = {"150cc": [], "200cc": []}
    for category in categories:
        for cc in ccs:
            for race in category:
                leaderboard = category[race]["Leaderboard"]
                if leaderboard[cc]:
                    if leaderboard[cc][0]["ID"] == discord_id:
                        ccs[cc] = True
                        records[cc].append(f"{race}")
                        print(f"{race} {cc}")
    
    for cc, value in ccs.items():
        if not value:
            print(f"You have no records for {cc}.")
    return records

def update_versus_rating(name=None, discord_id=None, v_rating=None):
    if not name or not v_rating:
        name, discord_id, v_rating = [part.strip() for part in input("What name, id and vr? (name, id, vr)").split(",")]
    vr = VersusRating(name, discord_id, v_rating)

    vr_list = [VersusRating.from_json(part) for part in VERSUS_RATINGS["vrs"]]

    # result = []

    for i, versus_rating in enumerate(vr_list):
        if vr.discord_id == versus_rating.discord_id:
            vr_list[i] = vr
            # print("Your rating has been updated!")
            status = "Your rating has been updated!"
            break
        if vr > versus_rating:
            status = f"You beat {versus_rating.name}."
            # print(f"You beat {versus_rating.name}.")
            for j, old_rating in enumerate(vr_list):
                if old_rating.discord_id == discord_id:
                    vr_list[j] = vr
                    break
            else:
                vr_list.insert(i, vr)
            break
    else:
        vr_list.append(vr)
        status = "Your rating has been added."
        # print("Your rating has been added.")

    vr_list.sort()
    vr_list.reverse()

    VERSUS_RATINGS["vrs"] = [vr.json for vr in vr_list]

    # vr_string = [str(vr) for vr in vr_list]

    # VERSUS_RATINGS["vrs"] = vr_string

    with open(Path.cwd().joinpath("data", "versus_rating.json"), "w") as outfile:
        json.dump(VERSUS_RATINGS, outfile, indent=4)

    # result.append(view_versus_rating(vr.discord_id, vr_list))
    # result = "\n".join(result)

    standing, leaderboard_title, leaderboard = view_versus_rating(vr.discord_id, vr_list)
    return status, standing, leaderboard_title, leaderboard

def view_versus_rating(discord_id=None, vr_list=None, all_places=False):
    places_to_display = 5
    if not discord_id:
        discord_id = input("What is your discord_id? ")
    if not vr_list:
        vr_list = [VersusRating.from_json(vr) for vr in VERSUS_RATINGS["vrs"]]

    if len(vr_list) < places_to_display or all_places:
        places_to_display = len(vr_list)

    for i, versus_rating in enumerate(vr_list):
        if versus_rating.discord_id == discord_id:
            if i == 0:
                standing = f"{versus_rating.name} is in {i + 1}. place with VR {versus_rating.vr}!"
                # print(f"You are in {i + 1}. place!")
            else:
                standing = f"{versus_rating.name} is in {i + 1}. place with VR {versus_rating.vr}, behind {vr_list[i - 1].name}."
                # print(f"You are in {i + 1}. place, behind {vr_list[i - 1].name}.")
            break
    else:
        standing = f"Couldn\'t find anyone with discord id: {discord_id}."
        # print(f"Couldn\'t find anyone named {name}.")

    if all_places:
        leaderboard_title = "All versus ratings:"
        # print("All versus ratings:")
    else:
        leaderboard_title = f"Top {places_to_display} versus ratings:"
        # print(f"Top {places_to_display} versus ratings:")

    leaderboard = []
    i = 1
    leaderboard.append(f"{i}. {vr_list[0]}")
    # print(f"{i}. {vr_list[0]}")
    for j in range(1, places_to_display):
        if vr_list[j - 1].vr != vr_list[j].vr:
            i = j + 1
        # print(f"{i}. {vr_list[j]}")
        leaderboard.append(f"{i}. {vr_list[j]}")

    leaderboard = "\n".join(leaderboard)

    # TODO Should just return a leaderboard dict, that can be directly used in make_embed()
    return standing, leaderboard_title, leaderboard

def setup(bot):
    bot.add_cog(Leaderboard(bot))

if __name__ == '__main__':
    add_record()
    # view_course_records()
    # count_personal_records()
    # view_personal_records()
    # print(update_versus_rating())
    # print(view_versus_rating(all_places=True))
    