import unittest
from pathlib import Path
import json
# import sys, os
# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath + '/../')
# The above is not needed when using unittest and running tests from root directory

from cogs import leaderboard

class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        with open(Path.cwd().joinpath("tests", "fixtures", "tracks.json"), "r") as read_file:
            self.tracks = json.load(read_file)

        with open(Path.cwd().joinpath("tests", "fixtures", "aliases.json"), "r") as read_file:
            self.aliases = json.load(read_file)

        with open(Path.cwd().joinpath("tests", "fixtures", "cups.json"), "r") as read_file:
            self.cups = json.load(read_file)

        with open(Path.cwd().joinpath("tests", "fixtures", "speed_run_categories.json"), "r") as read_file:
            self.speed_run_categories = json.load(read_file)

        with open(Path.cwd().joinpath("tests", "fixtures", "versus_rating.json"), "r") as read_file:
            self.versus_ratings = json.load(read_file)

        Path("data").mkdir(exist_ok=True)

    def test_Record(self):
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

    def test_VersusRating(self):
        test_vr_1 = leaderboard.VersusRating("Roger", 123189, 1500)
        test_vr_2 = leaderboard.VersusRating("Liz", 123121, 1500)
        self.assertEqual(test_vr_1, test_vr_2)
        self.assertEqual("Roger: 1500", str(test_vr_1))
    
    def test_add_record(self):
        race_data = {}
        race_data["name"] = "Nitro"
        race_data["category_name"] = "test_speed_run_categories"
        race_data["category_data"] = self.speed_run_categories
        race_info, status, standing, leaderboard_titles, leaderboards = leaderboard.add_record(race_data, "Jane", 121212, "15:14.130", "150")
        race_info_correct = "Cups: Mushroom, Flower, Star, Special"
        status_correct = "You have the record!"
        standing_correct = "----------\n**150cc**: You are in 2. place, behind Dan.\n**200cc**: You are not on the leaderboard yet."
        leaderboard_titles_correct = {'150cc': 'Top 2 results (150cc)', '200cc': 'Top results (200cc)'}
        leaderboards_correct = {'150cc': '1. Dan: 10:12.213\n2. Jane: 15:14.130', '200cc': 'No records for 200cc yet!'}
        self.assertEqual(race_info, race_info_correct)
        self.assertEqual(status, status_correct)
        self.assertEqual(standing, standing_correct)
        self.assertEqual(leaderboard_titles, leaderboard_titles_correct)
        self.assertEqual(leaderboards, leaderboards_correct)
        Path.cwd().joinpath("data", race_data["category_name"] + ".json").unlink()

    # Not currently working, may be better to rewrite count_personal_records a bit.
    # def test_count_personal_records(self):
    #     count_pr = leaderboard.count_personal_records
    #     count_pr.categories = [self.tracks, self.cups, self.speed_run_categories]
    #     count_150, count_200 = count_pr(895961)
    #     self.assertEqual(count_150, 2)
    #     self.assertEqual(count_200, 0)

if __name__ == '__main__':
    unittest.main()
