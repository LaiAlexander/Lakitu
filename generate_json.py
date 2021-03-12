import json
import pathlib

CUPS = [
    "Mushroom",
    "Flower",
    "Star",
    "Special",
    "Shell",
    "Banana",
    "Leaf",
    "Lightning",
    "Egg",
    "Triforce",
    "Crossing",
    "Bell",
]
SPEED_RUN_CATEGORIES = ["Nitro", "Retro", "Extra", "48"]
CONSOLES = ["GBA", "N64", "SNES", "DS", "Wii", "3DS", "GCN"]


def generate_tracks():
    # Generate tracks
    with open("tracks.txt") as file:
        tracks = {}
        course_i = 0
        cup_i = 0
        i = 0
        for line in file.readlines():
            if line.strip() == "-":
                break
            tracks[line.strip()] = {
                "Cup": CUPS[cup_i],
                "Course": SPEED_RUN_CATEGORIES[course_i],
                "Alias": "",
                "Leaderboard": {
                    "150cc": [],
                    "200cc": [],
                },
            }

            i += 1
            if i % 16 == 0:
                course_i += 1
            if i % 4 == 0:
                cup_i += 1
    return tracks


def generate_aliases(tracks):
    # Generate aliases
    aliases = {}
    for track in tracks:
        track_name = [word for word in track.split(" ") if word not in CONSOLES]
        alias = "".join([word[0:2].lower() for word in track_name])
        prefix = tracks[track]["Course"][0].lower()
        alias = prefix + "-" + alias if prefix != "n" else alias
        aliases[alias] = track
        tracks[track]["Alias"] = alias
    return aliases


def generate_cups(tracks):
    # Generate cups
    cups = {
        key: {
            "Tracks": [],
            "Course": "",
            "Leaderboard": {
                "150cc": [],
                "200cc": [],
            },
        }
        for key in CUPS
    }

    for track in tracks:
        cup_name = tracks[track]["Cup"]
        cups[cup_name]["Tracks"].append(track)
        cups[cup_name]["Course"] = tracks[track]["Course"]

    return cups


def generate_speed_run_categories(tracks):
    # Generate speed_run_categories
    speed_run_categories = {
        key: {
            "Cups": [],
            "Leaderboard": {
                "150cc": [],
                "200cc": [],
            },
        }
        for key in SPEED_RUN_CATEGORIES
    }
    for track in tracks:
        category = tracks[track]["Course"]
        cup = tracks[track]["Cup"]
        if cup not in speed_run_categories[category]["Cups"]:
            speed_run_categories[category]["Cups"].append(tracks[track]["Cup"])
        if cup not in speed_run_categories["48"]["Cups"]:
            speed_run_categories["48"]["Cups"].append(tracks[track]["Cup"])
    return speed_run_categories


def generate_versus_rating():
    return {"vrs": []}


def generate_json():
    tracks = generate_tracks()
    aliases = generate_aliases(tracks)
    cups = generate_cups(tracks)
    speed_run_categories = generate_speed_run_categories(tracks)
    versus_rating = generate_versus_rating()

    pathlib.Path("data").mkdir(exist_ok=True)

    with open(pathlib.Path.cwd().joinpath("data", "tracks.json"), "w") as outfile:
        json.dump(tracks, outfile, indent=4)

    with open(pathlib.Path.cwd().joinpath("data", "aliases.json"), "w") as outfile:
        json.dump(aliases, outfile, indent=4)

    with open(pathlib.Path.cwd().joinpath("data", "cups.json"), "w") as outfile:
        json.dump(cups, outfile, indent=4)

    with open(
        pathlib.Path.cwd().joinpath("data", "speed_run_categories.json"), "w"
    ) as outfile:
        json.dump(speed_run_categories, outfile, indent=4)

    with open(
        pathlib.Path.cwd().joinpath("data", "versus_rating.json"), "w"
    ) as outfile:
        json.dump(versus_rating, outfile, indent=4)


if __name__ == "__main__":
    generate_json()
