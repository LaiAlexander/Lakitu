import unittest
from pathlib import Path
import json

import discord

# import sys, os
# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath + '/../')
# The above is not needed when using unittest and running tests from root directory

from cogs import leaderboard


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        with open(
            Path.cwd().joinpath("tests", "fixtures", "tracks.json"), "r"
        ) as read_file:
            self.tracks = json.load(read_file)

        with open(
            Path.cwd().joinpath("tests", "fixtures", "aliases.json"), "r"
        ) as read_file:
            self.aliases = json.load(read_file)

        with open(
            Path.cwd().joinpath("tests", "fixtures", "cups.json"), "r"
        ) as read_file:
            self.cups = json.load(read_file)

        with open(
            Path.cwd().joinpath("tests", "fixtures", "speed_run_categories.json"), "r"
        ) as read_file:
            self.speed_run_categories = json.load(read_file)

        with open(
            Path.cwd().joinpath("tests", "fixtures", "versus_rating.json"), "r"
        ) as read_file:
            self.versus_ratings = json.load(read_file)

        leaderboard.ALIASES = self.aliases
        leaderboard.TRACKS = self.tracks
        leaderboard.CUPS = self.cups
        leaderboard.SPEED_RUN_CATEGORIES = self.speed_run_categories
        leaderboard.VERSUS_RATINGS = self.versus_ratings

        Path("data").mkdir(exist_ok=True)

    def test_make_embed(self):
        correct_embed = leaderboard.discord.Embed(
            title="Title",
            description="Status\nStanding",
            color=leaderboard.discord.Color.blue(),
        )
        correct_embed.set_author(name="Claire", icon_url="icon_url")
        field_1 = {"name": "150cc", "value": "No entries"}
        field_2 = {"name": "200cc", "value": "No entries"}
        correct_embed.add_field(name=field_1["name"], value=field_1["value"])
        correct_embed.add_field(name=field_2["name"], value=field_2["value"])
        embed = leaderboard.make_embed(
            "Title", "Status", "Standing", "Claire", "icon_url", field_1, field_2
        )
        self.assertEqual(embed.title, correct_embed.title)
        self.assertEqual(embed.description, correct_embed.description)
        self.assertEqual(embed.color, correct_embed.color)
        self.assertEqual(embed.author.name, correct_embed.author.name)
        self.assertEqual(embed.author.icon_url, correct_embed.author.icon_url)
        self.assertEqual(embed.fields[0].name, correct_embed.fields[0].name)
        self.assertEqual(embed.fields[0].value, correct_embed.fields[0].value)
        self.assertEqual(embed.fields[1].name, correct_embed.fields[1].name)
        self.assertEqual(embed.fields[1].value, correct_embed.fields[1].value)

    def test_Record(self):
        # TODO test the rest of the methods
        test_record_1 = leaderboard.Record("John", 123189, "1:2:139")
        test_record_2 = leaderboard.Record("John", 123121, "1:2.139")
        self.assertEqual(test_record_1, test_record_2)
        self.assertEqual(test_record_1.time, leaderboard.datetime.time(0, 1, 2, 139000))
        self.assertEqual(test_record_1.time_to_str(), "01:02.139")
        record = {}
        record["Name"] = "John"
        record["ID"] = 123189
        record["Time"] = "01:02.139"
        self.assertDictEqual(test_record_1.json, record)
        record["ID"] = 123121
        test_record_3 = leaderboard.Record.from_json(record)
        self.assertIsInstance(test_record_3, leaderboard.Record)
        self.assertEqual(test_record_3, test_record_2)
        self.assertLessEqual(test_record_1, test_record_2)
        test_record_4 = leaderboard.Record("Tim", 123189, "1:2.130")
        self.assertLess(test_record_4, test_record_1)
        self.assertEqual(str(test_record_1), "John: 01:02.139")
        self.assertEqual(repr(test_record_1), "John: 00:01:02.139000")
        test_record_5 = leaderboard.Record("John", 123189, "1:15:23:142")
        self.assertEqual(test_record_5.time_to_str(), "01:15:23.142")

    def test_VersusRating(self):
        # TODO test the rest of the methods
        test_vr_1 = leaderboard.VersusRating("Roger", 123189, 1500)
        test_vr_2 = leaderboard.VersusRating("Liz", 123121, 1500)
        test_vr_3 = leaderboard.VersusRating("Mark", 123456, 1400)
        self.assertEqual(test_vr_1, test_vr_2)
        self.assertEqual("Roger: 1500", str(test_vr_1))
        self.assertLess(test_vr_3, test_vr_1)
        data = {"Name": "Gary", "ID": 654321, "vr": 1400}
        test_vr_4 = leaderboard.VersusRating.from_json(data)
        self.assertDictEqual(data, test_vr_4.json)

    def test_add_record(self):
        race_data = {}
        race_data["name"] = "Nitro"
        race_data["category_name"] = "test_speed_run_categories"
        race_data["category_data"] = self.speed_run_categories
        (
            race_info,
            status,
            standing,
            leaderboard_titles,
            leaderboards,
        ) = leaderboard.add_record(race_data, "Jane", 121212, "15:14.130", "150")
        race_info_correct = "Cups: Mushroom, Flower, Star, Special"
        status_correct = "You have the record!"
        standing_correct = (
            "----------\n**150cc**: You are in 2. place, behind Dan."
            "\n**200cc**: You are not on the leaderboard yet."
        )
        leaderboard_titles_correct = {
            "150cc": "Top 2 results (150cc)",
            "200cc": "Top results (200cc)",
        }
        leaderboards_correct = {
            "150cc": "1. Dan: 10:12.213\n2. Jane: 15:14.130",
            "200cc": "No records for 200cc yet!",
        }
        self.assertEqual(race_info, race_info_correct)
        self.assertEqual(status, status_correct)
        self.assertEqual(standing, standing_correct)
        self.assertEqual(leaderboard_titles, leaderboard_titles_correct)
        self.assertEqual(leaderboards, leaderboards_correct)

        (
            race_info,
            status,
            standing,
            leaderboard_titles,
            leaderboards,
        ) = leaderboard.add_record(race_data, "Jane", 121212, "09:14.130", "150")
        status_correct = "<@895961> has been beaten!"
        standing_correct = (
            "----------\n**150cc**: You are in 1. place!"
            "\n**200cc**: You are not on the leaderboard yet."
        )
        leaderboards_correct = {
            "150cc": "1. Jane: 09:14.130\n2. Dan: 10:12.213",
            "200cc": "No records for 200cc yet!",
        }
        self.assertEqual(status, status_correct)
        self.assertEqual(standing, standing_correct)
        self.assertEqual(leaderboards, leaderboards_correct)

        (
            race_info,
            status,
            standing,
            leaderboard_titles,
            leaderboards,
        ) = leaderboard.add_record(race_data, "Jane", 121212, "09:12.130", "150")
        status_correct = "You beat your own record!"
        leaderboards_correct = {
            "150cc": "1. Jane: 09:12.130\n2. Dan: 10:12.213",
            "200cc": "No records for 200cc yet!",
        }
        self.assertEqual(status, status_correct)
        self.assertEqual(leaderboards, leaderboards_correct)

        (
            race_info,
            status,
            standing,
            leaderboard_titles,
            leaderboards,
        ) = leaderboard.add_record(race_data, "Jane", 121212, "09:16.130", "150")
        status_correct = "Your previous record is better!"
        self.assertEqual(status, status_correct)

        Path.cwd().joinpath("data", race_data["category_name"] + ".json").unlink()

    def test_get_race_data(self):
        result = leaderboard.get_race_data("makast")
        result_correct = {
            "name": "Mario Kart Stadium",
            "category_name": "tracks",
            "category_data": leaderboard.TRACKS,
        }
        self.assertDictEqual(result, result_correct)
        result = leaderboard.get_race_data("Mario Kart Stadium")
        self.assertDictEqual(result, result_correct)
        result = leaderboard.get_race_data("mario kart stadium")
        self.assertDictEqual(result, result_correct)
        result = leaderboard.get_race_data("Mushroom")
        result_correct = {
            "name": "Mushroom",
            "category_name": "cups",
            "category_data": leaderboard.CUPS,
        }
        self.assertDictEqual(result, result_correct)
        result = leaderboard.get_race_data("Nitro")
        result_correct = {
            "name": "Nitro",
            "category_name": "speed_run_categories",
            "category_data": leaderboard.SPEED_RUN_CATEGORIES,
        }
        self.assertDictEqual(result, result_correct)
        result = leaderboard.get_race_data("Foo")
        self.assertIsNone(result)

    def test_get_cc(self):
        self.assertEqual(leaderboard.get_cc("150"), "150cc")
        self.assertEqual(leaderboard.get_cc("200"), "200cc")
        self.assertEqual(leaderboard.get_cc("300"), None)

    def test_view_course_records(self):
        # TODO implement this
        # Big parts of this is tested indirectly through test_add_record()
        pass

    def test_count_personal_records(self):
        # TODO implement this
        count_150, count_200 = leaderboard.count_personal_records(895961)
        self.assertEqual(count_150, 3)
        self.assertEqual(count_200, 1)

    def test_view_personal_records(self):
        correct_records = {
            "150cc": "Mario Kart Stadium\nFlower Cup\nNitro Tracks",
            "200cc": "Flower Cup",
        }
        records = leaderboard.view_personal_records(895961)
        self.assertDictEqual(correct_records, records)
        correct_records = {
            "150cc": "No records yet!",
            "200cc": "No records yet!",
        }
        records = leaderboard.view_personal_records(000000)
        self.assertDictEqual(correct_records, records)

    def test_update_versus_rating(self):
        # TODO implement this
        pass

    def test_view_versus_rating(self):
        standing, leaderboard_title, l_board = leaderboard.view_versus_rating(
            895961, all_places=True
        )
        correct_standing = "Tim is in 1. place with VR 6000!"
        correct_leaderboard_title = "All versus ratings:"
        correct_l_board = (
            "1. Tim: 6000\n2. Kate: 5600\n3. Mary: 5000\n"
            "4. Dan: 1909\n5. Roger: 1520\n6. Jenny: 1400"
        )
        self.assertEqual(correct_standing, standing)
        self.assertEqual(correct_leaderboard_title, leaderboard_title)
        self.assertEqual(correct_l_board, l_board)

        standing, leaderboard_title, l_board = leaderboard.view_versus_rating(577201)
        correct_standing = "Kate is in 2. place with VR 5600, behind Tim."
        correct_leaderboard_title = "Top 5 versus ratings:"
        correct_l_board = (
            "1. Tim: 6000\n2. Kate: 5600\n3. Mary: 5000\n4. Dan: 1909\n5. Roger: 1520"
        )
        self.assertEqual(correct_standing, standing)
        self.assertEqual(correct_leaderboard_title, leaderboard_title)
        self.assertEqual(correct_l_board, l_board)

        standing, leaderboard_title, l_board = leaderboard.view_versus_rating(100000)
        correct_standing = "Couldn't find anyone with discord id: 100000."
        self.assertEqual(correct_standing, standing)


if __name__ == "__main__":
    unittest.main()
