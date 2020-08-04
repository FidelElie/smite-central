import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib import admin
from django.conf import settings
from django.utils.timezone import make_aware

from esports.models import Competition, Match
from esports.youtubeAPI import YoutubeAPI
from esports.stringhelper import StringHelper

class Command(BaseCommand):

    base_page_token = "BASE"

    filters = {
        Competition.SMITE_PRO_LEAGUE: {
            "include": ["smite pro league", "spl"],
            "exclude": ["gauntlet", "relegations", "qualifiers", "show", "finals",  "clip", "cup", "cosplay", "predictions"]
        },
        Competition.SMITE_WORLD_CHAMPIONSHIP: {
            "include": ["smite world championship", "hrx"],
            "exclude": ["ceremony", "knockout", "placement", "xbox", "pre-game", "carpet", "console", "previews", "show", "cosplay"]
        }
    }

    match_data = []
    youtube_api = YoutubeAPI(settings.YOUTUBE_API_KEY)
    stringhelper = StringHelper()

    def handle(self, *args, **kwargs):
        self.stringhelper.add_regexp(
            "game-parts", "(\(?Game\s*\d+(\s*of\s*\d+\)?|\)|.*\))?)")
        self.stringhelper.add_regexp("number", "\d+")
        self.stringhelper.add_regexp("box-brackets", "\[+.*\]+")

        spl_league_regexp = "({}\:*\s+)".format(
            self.stringhelper.regexp_word_sequence(
                self.filters[Competition.SMITE_PRO_LEAGUE]["include"]
            ))

        swc_league_regexp = "({}\:*\s+".format(
            self.stringhelper.regexp_word_sequence(
                self.filters[Competition.SMITE_WORLD_CHAMPIONSHIP]["include"]
            ))

        self.stringhelper.add_regexp(
            Competition.SMITE_PRO_LEAGUE, spl_league_regexp)
        self.stringhelper.add_regexp(
            Competition.SMITE_WORLD_CHAMPIONSHIP, spl_league_regexp)

        self.get_competition_matches()
        self.get_remaining_matches()

        # Add values to the database
        Match.objects.all().delete()

        self.stdout.write("Sorting Data In Descending Season Order")
        sort_function = lambda x: x["competition"].season
        sorted_data = sorted(self.match_data, key=sort_function, reverse=True)

        self.stdout.write("Writing Data To Database")
        for data in sorted_data:
            Match(**data).save()

    def get_competition_matches(self):
        self.stdout.write("Collecting Competition Matches")

        competition_data = Competition.objects.all()

        for comp in competition_data:
            self.stdout.write(
                "Collecting Data For {} {}".format(comp.league, comp.season))

            page_token = self.base_page_token
            while page_token != None:
                page_token = None if page_token == "Base" else page_token

                api_parameters = {
                    "part": "snippet",
                    "playlistId": comp.playlist_id
                }

                if page_token != None:
                    api_parameters["pageToken"] = page_token

                video_batch = self.youtube_api.playlist_items(api_parameters)

                for video in video_batch["items"]:

                    video_title = self.stringhelper.remove_extra_spaces(
                        video["snippet"]["title"]
                    )

                    filter_check = self.stringhelper.filter_string(
                        video_title, self.filters[comp.league]
                    )

                    video_title = self.clean_string(video_title, comp.league)

                    if filter_check:
                        compound_games_flag = False
                        game_parts_re = self.stringhelper.regexps["game-parts"]
                        game_str_check = game_parts_re.findall(video_title)

                        if game_str_check:
                            compound_games_flag = True
                            video_title, game_number = \
                                self.strip_game_parts(video_title, game_str_check)

                        titles = [
                            m["title"].lower() for m in self.match_data
                        ]

                        title_present = video_title.lower() in titles

                        if title_present and compound_games_flag:
                            index = titles.index(video_title.lower())

                            ids = self.transpose_ids(
                                self.match_data[index]["ids"])

                            ids.insert(
                                game_number - 1,
                                video["snippet"]["resourceId"]["videoId"]
                            )

                            self.match_data[index]["ids"] = \
                                self.transpose_ids(ids)

                            if game_number == 1:
                                self.match_data[index]["thumbnail"]: \
                                    video["snippet"]["thumbnails"]["high"]["url"]
                        else:
                            self.match_data.append(
                                {
                                    "title": video_title,
                                    "ids": video["snippet"]["resourceId"]["videoId"],
                                    "competition": comp,
                                    "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                                    "date_published": \
                                        make_aware(
                                            YoutubeAPI.create_date_object(video["snippet"]["publishedAt"]))
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

        most_recent_comp = Competition.objects.get(
            league=Competition.SMITE_PRO_LEAGUE,
            season=max(season_numbers)
        )

        latest_season_video_dates = [
                index["date_published"] for index in self.match_data \
                if index["competition"] == most_recent_comp
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
                "part": "snippet"
            }

            if page_token != None:
                api_parameters["pageToken"] = page_token

            video_batch = self.youtube_api.search(api_parameters)

            for video in video_batch["items"]:
                video_title = self.stringhelper.remove_extra_spaces(
                    video["snippet"]["title"]
                )

                filter_check = self.stringhelper.filter_string(
                    video_title,
                    self.filters[most_recent_comp.league]
                )

                video_title = self.clean_string(
                    video_title, most_recent_comp.league)

                if filter_check:
                    titles = [d["title"].lower() for d in self.match_data]

                    if video_title.lower() not in titles:
                        self.match_data.append(
                            {
                                "title": video_title,
                                "ids": video["id"]["videoId"],
                                "competition": most_recent_comp,
                                "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                                "date_published": \
                                    make_aware(
                                        YoutubeAPI.create_date_object(video["snippet"]["publishedAt"])),
                            }
                        )

            if "nextPageToken" in video_batch:
                page_token = video_batch["nextPageToken"]
                index += 1
            else:
                break

        self.stdout.write("Collecting Remaining Matches Completed")

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
        league_regexp = self.stringhelper.regexps[league]
        stripped_league = league_regexp.sub("", string_to_clean)
        # Check If Comments In String
        box_bracket_regexp = self.stringhelper.regexps["box-brackets"]
        uncommented_string = box_bracket_regexp.sub("", stripped_league)
        # Remove Extra Spaces
        cleaned_string = self.stringhelper.remove_extra_spaces(
            uncommented_string)

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
        game_parts_regexp = self.stringhelper.regexps["game-parts"]
        number_regexp = self.stringhelper.regexps["number"]

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

