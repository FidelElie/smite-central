import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.timezone import make_aware

from esports.models import Competition, Match
from esports.youtubeAPI import YoutubeAPI
from esports.stringhelper import StringHelper

class Command(BaseCommand):
    help = "Update The Existing Matches Data"

    base_page_token = "BASE"

    filters = {
        Competition.CompetitionLeagues.SMITE_PRO_LEAGUE: {
            "include": ["smite pro league", "spl"],
            "exclude": ["gauntlet", "relegations", "qualifiers", "show", "finals",  "clip", "cup", "cosplay", "predictions"]
        },
        Competition.CompetitionLeagues.SMITE_WORLD_CHAMPIONSHIP: {
            "include": ["smite world championship", "hrx", "smite world championships"],
            "exclude": ["ceremony", "knockout", "placement", "xbox", "pre-game", "carpet", "console", "previews", "show", "cosplay"]
        },
        Competition.CompetitionLeagues.SMITE_CHALLENGER_CIRCUIT: {
            "include": ["smite challenger circuit", "scc"],
            "exclude": ["playoffs"]
        },
        Competition.CompetitionLeagues.SMITE_OPEN_CIRCUIT: {
            "include": ["smite open circuit", "soc"],
            "exclude": ["playoffs"]
        }
    }

    match_data = []
    youtube_api = YoutubeAPI(settings.YOUTUBE_API_KEY)
    string_helper = StringHelper()

    def add_arguments(self, parser):
        parser.add_argument("-f", "--flush", action="store_true", help="Flush Database Before Adding Database Entries")

    def handle(self, *args, **kwargs):
        flush = kwargs["flush"]
        self.create_translation_entities()

        self.string_helper.add_regexp(
            "game-parts", "(\(?Game\s*\d+(\s*of\s*\d+\)?|\)|.*\))?)")
        self.string_helper.add_regexp("number", "\d+")
        self.string_helper.add_regexp("box-brackets", "\[+.*\]+")

        for _filter in self.filters:
            include_filters = self.filters[_filter]["include"]
            sequence = self.string_helper.regexp_word_sequence(include_filters)
            reg_exp_str = "({}((\s*\:)+|( \s*\-)+|(\s+)+))"
            full_reg_exp_str = reg_exp_str.format(sequence)
            self.string_helper.add_regexp(_filter, full_reg_exp_str)


        competition_data = [comp for comp in Competition.objects.all() if comp.league in self.filters.keys()]

        if not competition_data:
            raise CommandError("No Competitions Present 'update-competitions'")

        self.get_competition_matches(competition_data)
        self.get_remaining_matches()

        # Add values to the database

        self.stdout.write("Sorting Data In Descending Season Order")

        sort_function = lambda x: x["competition"].season
        sorted_data = sorted(self.match_data, key=sort_function, reverse=True)

        if flush:
            self.stdout.write("Flushing Matches Table")
            Match.objects.all().delete()

        self.stdout.write("Updating Database With Matches")

        for data in sorted_data:
            existing_match = Match.objects.filter(ids=data["ids"])
            if not existing_match.exists():
                Match(**data).save()

        self.stdout.write("Database Update Was Successful")

    def get_competition_matches(self, competition_data):
        """ Get Matches Based On Present Competitions Saved

        Parameters
        ----------
        competition_data: Queryset
            Database set of saved competitions.
        """
        self.stdout.write("Collecting Competition Matches")

        for comp in competition_data:
            self.stdout.write(f"Data Fetch For {comp.league} {comp.season}")

            page_token = self.base_page_token

            while page_token != None:
                page_token = None if page_token == "BASE" else page_token

                api_parameters = {
                    "part": "snippet",
                    "playlistId": comp.playlist_id,
                    "maxResults": 50
                }

                if page_token != None:
                    api_parameters["pageToken"] = page_token

                video_batch = self.youtube_api.playlist_items(api_parameters)

                for video in video_batch["items"]:
                    snippet = video["snippet"]

                    video_title = self.string_helper.remove_extra_spaces(
                        snippet["title"]
                    )

                    filter_check = self.string_helper.filter_string(
                        video_title, self.filters[comp.league]
                    )

                    video_title = self.clean_string(video_title, comp.league)

                    if filter_check:
                        games_parts = False
                        game_parts_re = self.string_helper.regexp("game-parts")
                        game_str_check = game_parts_re.findall(video_title)

                        if game_str_check:
                            game_parts = True
                            video_title, game_numb = self.strip_game_parts(
                                    video_title, game_str_check)

                        titles = [m["title"].lower() for m in self.match_data]

                        title_present = video_title.lower() in titles

                        if title_present and game_parts:
                            video_id = snippet["resourceId"]["videoId"]
                            index = titles.index(video_title.lower())

                            match_ids = self.match_data[index]["ids"]
                            ids_list = self.transpose_ids(match_ids)

                            if video_id not in ids_list:
                                ids_list.insert(game_numb - 1, video_id)

                            ids_str = self.transpose_ids(ids_list)
                            self.match_data[index]["ids"] = ids_str

                            if game_numb == 1:
                                thumb = snippet["thumbnails"]["high"]["url"]
                                self.match_data[index]["thumbnail"] = thumb
                        else:
                            video_id = snippet["resourceId"]["videoId"]
                            thumbnail = snippet["thumbnails"]["high"]["url"]
                            date = YoutubeAPI.create_date_object(
                                snippet["publishedAt"])
                            aware_date = make_aware(date)
                            self.match_data.append(
                                {
                                    "title": video_title,
                                    "ids": video_id,
                                    "competition": comp,
                                    "thumbnail": thumbnail,
                                    "date_published": aware_date
                                }
                            )

                if "nextPageToken" in video_batch:
                    page_token = video_batch["nextPageToken"]
                else:
                    break

        self.stdout.write("Collecting Competition Matches Completed")

    def get_remaining_matches(self):
        self.stdout.write("Collecting Remaining Matches")

        season_numbers = set(
            [numb["competition"].season for numb in self.match_data])

        most_recent_comps = Competition.objects.filter(season=
            max(season_numbers))

        comps_codes = [comp.league for comp in most_recent_comps]
        comps_regs = [self.string_helper.regexp(code) for code in comps_codes]

        latest_season_video_dates = [
            index["date_published"] for index in self.match_data \
            if index["competition"] in most_recent_comps
        ]

        earliest_date = min(latest_season_video_dates)
        earliest_date_string = YoutubeAPI.create_date_string(earliest_date)

        index = 1
        page_token = self.base_page_token
        while page_token != None:
            page_token = None if page_token == "BASE" else page_token

            self.stdout.write("Fetching Video From Page {}".format(index))

            api_parameters = {
                "channelId": settings.SMITE_VOD_ID,
                "maxResults": 50,
                "publishedAfter": earliest_date_string,
                "type": "video",
                "part": "snippet",
                "pageToken": page_token
            }

            video_batch = self.youtube_api.search(api_parameters)

            for video in video_batch["items"]:
                snippet = video["snippet"]
                video_title = self.string_helper.remove_extra_spaces(
                    snippet["title"]
                )

                reg_matches = [reg.search(video_title) for reg in comps_regs]

                def check_for_match(regexes):
                    for i, reg in enumerate(regexes):
                        if reg is not None:
                            return i

                league_index = check_for_match(reg_matches)
                league = most_recent_comps[league_index].league
                league_filter = self.filters[league]

                filter_check = self.string_helper.filter_string(
                    video_title, league_filter
                )

                video_title = self.clean_string(video_title, league)

                if filter_check:
                    game_parts = False
                    game_parts_re = self.string_helper.regexp("game-parts")
                    game_str_check = game_parts_re.findall(video_title)

                    if game_str_check:
                        game_parts = True
                        video_title, game_numb = self.strip_game_parts(
                            video_title, game_str_check
                        )

                    titles = [m["title"].lower() for m in self.match_data]

                    title_present = video_title.lower() in titles

                    if title_present and game_parts:
                        video_id = video["id"]["videoId"]
                        index = titles.index(video_title.lower())

                        match_ids = self.match_data[index]["ids"]
                        ids_list = self.transpose_ids(match_ids)

                        if video_id not in ids_list:
                            ids_list.insert(game_numb - 1, video_id)

                        ids_str = self.transpose_ids(ids_list)
                        self.match_data[index]["ids"] = ids_str

                        if game_numb == 1:
                            thumb = snippet["thumbnails"]["high"]["url"]
                            self.match_data[index]["thumbnail"] = thumb
                    elif not title_present:
                        video_id = video["id"]["videoId"]
                        thumbnail = snippet["thumbnails"]["high"]["url"]
                        date = YoutubeAPI.create_date_object(
                            snippet["publishedAt"])
                        aware_date = make_aware(date)
                        self.match_data.append(
                            {
                                "title": video_title,
                                "ids": video["id"]["videoId"],
                                "competition": most_recent_comps[league_index],
                                "thumbnail": thumbnail,
                                "date_published": aware_date
                            }
                        )


            if "nextPageToken" in video_batch:
                page_token = video_batch["nextPageToken"]
                index += 1
            else:
                break

        self.stdout.write("Collecting Remaining Mathces Completed")

    def clean_string(self, string_to_clean, league):
        """ Clean String From Patterns That Result From Human Error

        Parameters
        ----------
        string_to_clean: str
            String that needs to be clean

        Returns
        -------
        cleaned_string: str
            String with the extra information removed.

        Comments
        --------
        Some strings that are returned by the api will have varying titles based on human error. Such as double space between words and varying letter cases. This needs to be removed 'cleaned' so sensible comparisions can be made between strings.
        """
        # Remove League
        league_regexp = self.string_helper.regexps[league]
        stripped_league = league_regexp.sub("", string_to_clean)
        # Check If Comments In String
        box_bracket_regexp = self.string_helper.regexps["box-brackets"]
        uncommented_string = box_bracket_regexp.sub("", stripped_league)
        # Remove Extra Spaces
        stripped_entities = uncommented_string.replace("amp;", "")
        cleaned_string = self.string_helper.remove_extra_spaces(
            stripped_entities)

        return cleaned_string

    def strip_game_parts(self, title, reg_match):
        """ Seperate Important Video Title Data

        Parameters
        ----------
        title: str
            Title to strip of unwanted information
        reg_match: list
            Match object for given title string

        Returns
        -------
        stripped_title: str
            String stripped of unwanted information
        game_number: int
            Game number contained in a video title

        Comments
        --------
            For vidoes with multiple parts, the function will remove the Game number indicator e.g (Game 1) etc. So the same matches can be grouped.
        """
        game_parts_regexp = self.string_helper.regexps["game-parts"]
        number_regexp = self.string_helper.regexps["number"]

        tuple_match = reg_match[0]
        largest_match = max(tuple_match, key=len)
        game_number = int(number_regexp.findall(largest_match)[0])

        stripped_title = title.replace(largest_match, "").strip()
        return stripped_title, game_number

    @staticmethod
    def transpose_ids(ids):
        """ Changes the data type of given data.

        Parameters
        ----------
        ids: str or list
            The ids in different data formats

        Returns
        -------
        transposed_ids: list or str
            The ids in the opposite format.

        Comments
        --------
            This is used to keep ids in the database friendly string format and the easily modified list format.
        """
        if isinstance(ids, str):
            if "," in ids:
                transposed_ids = ids.split(",")
            else:
                transposed_ids = [ids]
        elif isinstance(ids, list):
            transposed_ids = ",".join(ids)
        else:
            raise TypeError("Can Only Transpose Ids Between Strings and Lists")

        return transposed_ids

