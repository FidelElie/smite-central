import re

from django.test import TestCase

from .models import Competition
from .stringhelper import StringHelper
# Create your tests here.

class StringHelperTestCases(TestCase):
    filter_map = {
        Competition.SMITE_PRO_LEAGUE: {
            "include": ["smite pro league", "spl"],
            "exclude": ["gauntlet", "relegations", "qualifiers", "show", "finals",  "clip", "cup", "cosplay", "predictions"]
        },
        Competition.SMITE_WORLD_CHAMPIONSHIP: {
            "include": ["smite world championship", "hrx"],
            "exclude": ["ceremony", "knockout", "placement", "xbox", "pre-game", "carpet", "console", "previews", "show", "cosplay"]
        }
    }

    def test_filter_string_inclusion(self):
        string = "Smite World Championship 2016 - Grand Finals (Game 5 of 5)"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.SMITE_WORLD_CHAMPIONSHIP])

        self.assertTrue(match)

    def test_filter_string_exclusion_1(self):
        string = "Super Regionals Day 6 - EU Grand Final Game 4"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.SMITE_PRO_LEAGUE]
        )
        self.assertFalse(match)

    def test_filter_string_exclusion_2(self):
        string = "Smite World Championship 2016 Day 3 - Cosplay"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.SMITE_PRO_LEAGUE]
        )

        self.assertFalse(match)

    def test_remove_extra_space(self):
        string = "Smite  World Championships   2015"

        self.assertEqual(
            StringHelper.remove_extra_spaces(string),
            "Smite World Championships 2015"
        )


    def test_regular_expressions(self):
        string_helper = StringHelper()
        string_helper.add_regexp("number", "\d+")
        returned_regexp = string_helper.regexps["number"]

        self.assertEqual(
            returned_regexp,
            re.compile("\d+", re.IGNORECASE)
        )


