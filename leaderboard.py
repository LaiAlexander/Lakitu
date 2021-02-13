import datetime
import json

with open("tracks.json", "r") as read_file:
    TRACKS = json.load(read_file)

with open("aliases.json", "r") as read_file:
    ALIASES = json.load(read_file)

with open("cups.json", "r") as read_file:
    CUPS = json.load(read_file)

with open("speed_run_categories.json", "r") as read_file:
    SPEED_RUN_CATEGORIES = json.load(read_file)

with open("versus_rating.json", "r") as read_file:
    VERSUS_RATINGS = json.load(read_file)

class Record():
    def __init__(self, name, time):
        self.name = name
        time = time.replace(".", ":")
        time = time.split(":")
        if len(time) == 3:
            time.insert(0, "0")
        if len(time[3]) < 3:
            if len(time[3]) < 2:
                time[3] = time[3] + "0"
            time[3] = time[3] + "0"
        self.time = datetime.datetime.strptime((":").join(time), "%H:%M:%S:%f").time()
        # should this be a time or a datetime object?

        # hour, minute, second, millisecond = [int(t) for t in time]
        # if millisecond < 1000:
        #     microsecond = millisecond * 1000
        # else:
        #     microsecond = millisecond
        # time = datetime.time(hour, minute, second, microsecond)
        # self.time = time

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
        time = record_dict["Time"]
        # time = time.split(".")
        # if len(time) > 1:
        #     time2 = time[1]
        #     time = time[0].split(":")
        #     time.append(time2)
        # else:
        #     time = time[0].split(":")
        # time = time.replace(".", ":")
        # time = time.split(":")
        # # time = [int(t) for t in time]
        # # print(time)
        # if len(time) < 4:
        #     # if len(time) < 3:
        #     #     if len(time) < 2:
        #     #         time.append("0")
        #     #     time.append("0")
        #     time.append("0")
        # # print(time)
        # time = (":").join(time)
        return cls(name, time)

class VersusRating():
    def __init__(self, name, vr):
        self.name = name
        self.vr = int(vr)

    def __lt__(self, value):
        return self.vr < value.vr

    def __eq__(self, value):
        return self.vr == value.vr

    def __str__(self):
        return f"{self.name}: {self.vr}"

    @classmethod
    def from_str(cls, data):
        name, vr = data.split(": ")
        return cls(name, vr)

def add_record():
    race_name, name, time, cc = [part.strip() for part in input("Shorthand for registering: (trackname/alias, name, time, cc):").split(",")]
    race_name, category_name, category = get_race_name(race_name)
    if not race_name:
        return
    race = category[race_name]
    ccs = ["150", "200"]
    if cc not in ccs:
        print("Not valid cc")
        return
    cc = cc + "cc"

    record = Record(name, time)

    record_list = [Record.from_json(records) for records in race["Leaderboard"][cc]]
    for i, existing_record in enumerate(record_list):
        if record < existing_record:
            if record.name == existing_record.name:
                record_list[i] = record
                print("You beat your own record!")
                break
            for old_record in record_list:
                if old_record.name == record.name:
                    print("This was identical")
                    record_list.remove(old_record)
                    break
            record_list.insert(i, record)
            print(existing_record.name + " have been beaten!")
            break
        if record.name == existing_record.name:
            print("Your previous record is better!")
            break
    else:
        record_list.append(record)
        print("You have the record!")
    record_list.sort()
    race["Leaderboard"][cc] = [{"Name": record.name, "Time": record.time_to_str()} for record in record_list]
    view_course_records(race_name, category, category_name, cc[:-2], name)
    with open(category_name + ".json", "w") as outfile:
        json.dump(category, outfile, indent=4)

def get_race_name(name):
    if ALIASES.get(name):
        name = ALIASES[name]
    name = name.title()
    if TRACKS.get(name):
        return name, "tracks", TRACKS
    if CUPS.get(name):
        return name, "cups", CUPS
    if SPEED_RUN_CATEGORIES.get(name):
        return name, "speed_run_categories", SPEED_RUN_CATEGORIES
    print("Not valid track/cup/category name.")
    return None, None, None

def get_cc(cc):
    valid_cc = ["150", "200"]
    if cc not in valid_cc:
        print("Not valid cc.")
        return None
    return cc + "cc"

def view_course_records(race_name=None, category=None, category_name=None, cc=None, name=None):
    places_to_display = 5
    
    if not race_name or not category or not category_name or not cc:
        race_name, cc = [part.strip() for part in input("What track and cc? (trackname/alias, cc) ").split(",")]
        race_name, category_name, category = get_race_name(race_name)
    if not name:
        name = input("What is your name? ")
    if not race_name:
        return

    race = category[race_name]

    cc = get_cc(cc)
    if not cc:
        return

    if category_name == "tracks":
        print(f"{race_name} {cc}, {race['Cup']} cup, {race['Course']} course.")
        print(f"Alias: {race['Alias']}")
    elif category_name == "cups":
        trks = (", ").join(race["Tracks"])
        print(f"{race_name} cup, {race['Course']} courses.")
        print(f"{trks}")
    elif category_name == "speed_run_categories":
        print(f"Speed run category: {race_name}.")
        print(f"Cups: {(', ').join(race['Cups'])}")

    record_list = race["Leaderboard"][cc]
    if not record_list:
        print("No records added yet!")
        return

    if len(record_list) < places_to_display:
        places_to_display = len(record_list)

    for i , record in enumerate(record_list):
        if record["Name"] == name:
            if i == 0:
                print(f"You are in {i + 1}. place!")
            else:
                print(f"You are in {i + 1}. place, behind {record_list[i - 1]['Name']}.")
            break

    print(f"Top {places_to_display} results:")
    i = 1
    print(f"{i}. {Record.from_json(record_list[0])}")
    for j in range(1, places_to_display):
        if record_list[j - 1]["Time"] != record_list[j]["Time"]:
            i = j + 1
        print(f"{i}. {Record.from_json(record_list[j])}")

def count_personal_records(name=None):
    if not name:
        name = input("What name? ")
    count_150 = 0
    count_200 = 0
    categories = [TRACKS, CUPS, SPEED_RUN_CATEGORIES]

    for category in categories:
        for race in category:
            leaderboard = category[race]["Leaderboard"]
            for cc, records in leaderboard.items():
                for record in records:
                    if record["Name"] == name and cc == "150cc":
                        count_150 += 1
                    if record["Name"] == name and cc == "200cc":
                        count_200 += 1
    print(f"150: {count_150} 200: {count_200}")

def view_personal_records():
    name = input("What name?")
    ccs = {"150cc": False, "200cc": False}
    categories = [TRACKS, CUPS, SPEED_RUN_CATEGORIES]
    for category in categories:
        for cc in ccs:
            for race in category:
                leaderboard = category[race]["Leaderboard"]
                if leaderboard[cc]:
                    if leaderboard[cc][0]["Name"] == name:
                        ccs[cc] = True
                        print(f"{race} {cc}")
    
    for cc, value in ccs.items():
        if not value:
            print(f"You have no records for {cc}.")

def update_versus_rating():
    name, v_rating = [part.strip() for part in input("What name and vr? (name, vr)").split(",")]
    vr = VersusRating(name, v_rating)
    
    vr_list = [VersusRating.from_str(part) for part in VERSUS_RATINGS["vrs"]]
    
    for i, versus_rating in enumerate(vr_list):
        if vr.name == versus_rating.name:
            print("Your rating has been updated!")
            vr_list[i] = vr
            break
        if vr > versus_rating:
            print(f"You beat {versus_rating.name}.")
            for j, old_rating in enumerate(vr_list):
                if old_rating.name == vr.name:
                    vr_list[j] = vr
                    break
            vr_list.insert(i, vr)
            break
    else:
        vr_list.append(vr)
        print("Your rating has been added")
    
    vr_list.sort()
    vr_list.reverse()

    vr_string = [str(vr) for vr in vr_list]

    VERSUS_RATINGS["vrs"] = vr_string
    
    view_versus_rating(vr.name)

    with open("versus_rating.json", "w") as outfile:
        json.dump(VERSUS_RATINGS, outfile, indent=4)

def view_versus_rating(name=None, vr_list=None):
    places_to_display = 5
    if not name:
        name = input("What is your name? ")

    vr_list = [VersusRating.from_str(vr) for vr in VERSUS_RATINGS["vrs"]]

    if len(vr_list) < places_to_display:
        places_to_display = len(vr_list)

    for i, versus_rating in enumerate(vr_list):
        if versus_rating.name == name:
            if i == 0:
                print(f"You are in {i + 1}. place!")
            else:
                print(f"You are in {i + 1}. place, behind {vr_list[i - 1].name}.")
            break
    else:
        print(f"Couldn\'t find anyone named {name}.")

    print(f"Top {places_to_display} versus ratings:")
    i = 1
    print(f"{i}. {vr_list[0]}")
    for j in range(1, places_to_display):
        if vr_list[j - 1].vr != vr_list[j].vr:
            i = j + 1
        print(f"{i}. {vr_list[j]}")

if __name__ == '__main__':
    # add_record()
    # view_course_records()
    # count_personal_records()
    # view_personal_records()
    # update_versus_rating()
    view_versus_rating()
