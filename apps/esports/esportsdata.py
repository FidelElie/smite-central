from django.conf import settings
from django.core.management.base import CommandError
from django.utils.timezone import make_aware

from esports.models import League, Competition, Match
from esports.youtubeAPI import YoutubeAPI
from esports.stringhelper import StringHelper

class EsportsData(object):

    data = []
    string_helper = StringHelper()
    youtube_api = YoutubeAPI(settings.YOUTUBE_API_KEY)
    base_page_token = "BASE"
    leagues = League.objects.all()
    filters = None

    def fetch_data(self):
        raise NotImplementedError("Method Must Be Reimplemented In Base Class")

    def commit_data(self):
        raise NotImplementedError("Method Must Be Reimplemented In Base Class")

    def flush_model(self):
        self.corresponding_model.objects.all().delete()

class CompetitionData(EsportsData):
    corresponding_model = Competition

    def fetch_data(self):
        league_titles = [league.title.lower() for league in self.leagues]

        self.filters = {
            league.code: {
                "include": league.competition_include_filters,
                "exclude": league.competition_exclude_filters
            } for league in self.leagues
        }

        print("Collecting Smite Competition Playlists")

        page_token = self.base_page_token
        while page_token != None:
            page_token = None if page_token == "BASE" else page_token

            api_parameters = {
                "part": "snippet",
                "channelId": settings.SMITE_VOD_ID,
                "pageToken": page_token,
                "maxResults": 50
            }

            playlist_batch = self.youtube_api.playlists(api_parameters)

            for playlist in playlist_batch["items"]:
                playlist_title = playlist["snippet"]["title"].lower()

                filter_check = self.string_helper.filter_string(
                    playlist_title,
                    self.string_helper.compound_filter(self.filters)
                )

                if filter_check:
                    season_number = playlist_title.split("season")[-1].strip()
                    title_in = lambda x: x in playlist_title
                    league_index = league_titles.index(
                        list(filter(title_in, league_titles))[0]
                    )
                    corresponding_league = self.leagues[league_index]

                    self.data.append({
                        "season": season_number,
                        "league": corresponding_league,
                        "playlist_id": playlist["id"]
                    })

            if "nextPageToken" in playlist_batch:
                page_token = playlist_batch["nextPageToken"]
            else:
                break

    def commit_data(self):
        print("Updating Competition Models With Entries")
        for data in self.data:
            existing_comp = self.corresponding_model.objects.filter(
                playlist_id=data["playlist_id"])

            if not existing_comp.exists():
                print("Adding {} {} To Competition Model".format(
                    data["league"], data["season"]
                ))
                Competition(**data).save()

        print("Competition Table Has Been Updated")

class MatchData(EsportsData):
    corresponding_model = Match

    def fetch_data(self):
        self.string_helper.add_regexp(
            "game-parts", "(\(?Game\s*\d+(\s*of\s*\d+\)?|\)|.*\))?)")
        self.string_helper.add_regexp("number", "\d+")
        self.string_helper.add_regexp("box-brackets", "\[+.*\]+")

        self.filters = {
            league.code: {
                "include": league.match_include_filters,
                "exclude": league.match_exclude_filters
            } for league in self.leagues
        }

        for _filter in self.filters:
            include_filters = self.filters[_filter]["include"]
            sequence = self.string_helper.regexp_word_sequence(include_filters)
            reg_exp_str = "({}((\s*\:)+|( \s*\-)+|(\s+)+))"
            full_reg_exp_str = reg_exp_str.format(sequence)
            self.string_helper.add_regexp(_filter, full_reg_exp_str)

        competition_data = [
            comp for comp in Competition.objects.all() if comp.league.code in self.filters.keys()]

        if not competition_data:
            raise CommandError("No Competitions Present 'update-competitions")

        print("Collecting Competition Matches")
        self.get_competition_matches(competition_data)
        print("Collecting Competition Matches Completed")

        print("Collecting Remaining Matches")
        self.get_remaining_matches()
        print("Collecting Remaining Mathces Completed")

    def commit_data(self):
        sort_function = lambda x: x["competition"].season
        sorted_data = sorted(self.data, key=sort_function, reverse=True)

        for data in sorted_data:
            existing_match = Match.objects.filter(ids=data["ids"])
            if not existing_match.exists():
                Match(**data).save()

        print("Match Table Has Been Updated")

    def get_competition_matches(self, competition_data):
        for comp in competition_data:
            print(f"Data Fetch For {comp.league.code} {comp.season}")

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
                        video_title, self.filters[comp.league.code]
                    )

                    video_title = self.clean_string(
                        video_title, comp.league.code)

                    if filter_check:
                        games_parts = False
                        game_parts_re = self.string_helper.regexp("game-parts")
                        game_str_check = game_parts_re.findall(video_title)

                        if game_str_check:
                            game_parts = True
                            video_title, game_numb = self.strip_game_parts(
                                    video_title, game_str_check)


                        titles = [m["title"].lower() for m in self.data]

                        title_present = video_title.lower() in titles

                        if title_present and game_parts:
                            video_id = snippet["resourceId"]["videoId"]
                            index = titles.index(video_title.lower())

                            match_ids = self.data[index]["ids"]

                            if video_id not in match_ids:
                                match_ids.insert(game_numb - 1, video_id)

                            self.data[index]["ids"] = match_ids

                            if game_numb == 1:
                                thumb = snippet["thumbnails"]["high"]["url"]
                                self.data[index]["thumbnail"] = thumb
                        else:
                            video_id = snippet["resourceId"]["videoId"]
                            thumbnail = snippet["thumbnails"]["high"]["url"]
                            date = YoutubeAPI.create_date_object(
                                snippet["publishedAt"])
                            aware_date = make_aware(date)
                            self.data.append(
                                {
                                    "title": video_title,
                                    "ids": [video_id],
                                    "competition": comp,
                                    "thumbnail": thumbnail,
                                    "date_published": aware_date
                                }
                            )

                if "nextPageToken" in video_batch:
                    page_token = video_batch["nextPageToken"]
                else:
                    break

    def get_remaining_matches(self):
        season_numbers = set(
            [numb["competition"].season for numb in self.data])

        most_recent_comps = Competition.objects.filter(season=
            max(season_numbers))

        comps_codes = [comp.league.code for comp in most_recent_comps]
        comps_regs = [self.string_helper.regexp(code) for code in comps_codes]

        latest_season_video_dates = [
            index["date_published"] for index in self.data \
            if index["competition"] in most_recent_comps
        ]

        earliest_date = min(latest_season_video_dates)
        earliest_date_string = YoutubeAPI.create_date_string(earliest_date)

        index = 1
        page_token = self.base_page_token
        while page_token != None:
            page_token = None if page_token == "BASE" else page_token

            print("Fetching Video From Page {}".format(index))

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

                league_index = self.check_for_match(reg_matches)
                if league_index == None:
                    continue

                league_code = most_recent_comps[league_index].league.code
                league_filter = self.filters[league_code]

                filter_check = self.string_helper.filter_string(
                    video_title, league_filter
                )

                video_title = self.clean_string(video_title, league_code)

                if filter_check:
                    game_parts = False
                    game_parts_re = self.string_helper.regexp("game-parts")
                    game_str_check = game_parts_re.findall(video_title)

                    if game_str_check:
                        game_parts = True
                        video_title, game_numb = self.strip_game_parts(
                            video_title, game_str_check
                        )

                    titles = [m["title"].lower() for m in self.data]

                    title_present = video_title.lower() in titles

                    if title_present and game_parts:
                        video_id = video["id"]["videId"]
                        index = titles.index(video_title.lower())

                        match_ids = self.data[index]["ids"]

                        if video_id not in match_ids:
                            match_ids.insert(game_numb - 1, video_id)

                        self.data["index"]["ids"] = match_ids

                        if game_numb == 1:
                            thumb = snippet["thumbnails"]["high"]["url"]
                            self.data[index]["thumbnail"] = thumb

                    elif not title_present:
                        video_id = video["id"]["videoId"]
                        thumbnail = snippet["thumbnails"]["high"]["url"]
                        date = YoutubeAPI.create_date_object(
                            snippet["publishedAt"])
                        aware_date = make_aware(date)
                        self.data.append(
                            {
                                "title": video_title,
                                "ids": [video_id],
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
    def check_for_match(regexes):
        for i, reg in enumerate(regexes):
            if reg is not None:
                return i
        else:
            return None
