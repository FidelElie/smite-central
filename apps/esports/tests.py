import re

from django.test import TestCase

from .models import Competition
from .stringhelper import StringHelper
# Create your tests here.

class StringHelperTestCases(TestCase):
    filter_map = {
        Competition.CompetitionLeagues.SMITE_PRO_LEAGUE: {
            "include": ["smite pro league", "spl"],
            "exclude": ["gauntlet", "relegations", "qualifiers", "show", "finals",  "clip", "cup", "cosplay", "predictions"]
        },
        Competition.CompetitionLeagues.SMITE_WORLD_CHAMPIONSHIP: {
            "include": ["smite world championship", "hrx"],
            "exclude": ["ceremony", "knockout", "placement", "xbox", "pre-game", "carpet", "console", "previews", "show", "cosplay"]
        },
        Competition.CompetitionLeagues.SMITE_CHALLENGER_CIRCUIT: {
            "include": ["smite challenger circuit", "scc"],
            "exclude": ["playoffs", "qualifiers"]
        },
        Competition.CompetitionLeagues.SMITE_OPEN_CIRCUIT: {
            "include": ["smite open circuit", "soc"],
            "exclude": ["playoffs", "qualifiers"]
        }
    }

    def test_filter_string_inclusion_1(self):
        string = "Smite World Championship 2016 - Grand Finals (Game 5 of 5)"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_WORLD_CHAMPIONSHIP])

        self.assertTrue(match)

    def test_filter_string_inclusion_2(self):
        string = "SMITE Challenger Circuit: Hype Unit vs Baskin and the Boys (Season 7 Phase 2 Week 1)"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_CHALLENGER_CIRCUIT]
        )

        self.assertTrue(match)

    def test_filter_string_exclusion_1(self):
        string = "Super Regionals Day 6 - EU Grand Final Game 4"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_PRO_LEAGUE]
        )
        self.assertFalse(match)

    def test_filter_string_exclusion_2(self):
        string = "Smite World Championship 2016 Day 3 - Cosplay"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_PRO_LEAGUE]
        )

        self.assertFalse(match)

    def test_filter_string_exclusion_3(self):
        string = "SCC 2020 Qualifiers: (NA) Round Robin Group 2 - Houdini's vs. Bloogy and the Woogys"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_CHALLENGER_CIRCUIT]
        )

        self.assertFalse(match)

    def test_filter_string_exclusion_4(self):
        string = "SMITE Challenger Circuit: Snake Pit vs The Papis (S7 Phase 3 Week 2)"

        match = StringHelper.filter_string(
            string, self.filter_map[Competition.CompetitionLeagues.SMITE_PRO_LEAGUE]
        )

        self.assertFalse(match)

    def test_remove_extra_space(self):
        string = "Smite  World Championships   2015"

        self.assertEqual(
            StringHelper.remove_extra_spaces(string),
            "Smite World Championships 2015"
        )

    def test_regexp_word_sequence(self):
        spl_str = Competition.CompetitionLeagues.SMITE_PRO_LEAGUE
        spl_includes = self.filter_map[spl_str]["include"]
        sequence = StringHelper.regexp_word_sequence(spl_includes)

        self.assertEqual(
            sequence,
            "(smite\s*pro\s*league|spl)"
        )


    def test_regular_expressions(self):
        string_helper = StringHelper()
        string_helper.add_regexp("number", "\d+")
        returned_regexp = string_helper.regexps["number"]

        self.assertEqual(
            returned_regexp,
            re.compile("\d+", re.IGNORECASE)
        )


