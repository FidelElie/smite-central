from django.core.management.base import BaseCommand, CommandError
from django.contrib import admin
from django.conf import settings

from esports.models import Competition
from esports.youtubeAPI import YoutubeAPI
from esports.stringhelper import StringHelper

class Command(BaseCommand):
    help = "Update The Exisiting Competition Data"

    filters = {
        Competition.CompetitionLeagues.SMITE_PRO_LEAGUE: {
            "include": ["smite pro league -"],
            "exclude": ["week"]
        },
        Competition.CompetitionLeagues.SMITE_WORLD_CHAMPIONSHIP: {
            "include": ["smite world championship -"],
            "exclude": ["week"]
        }
    }

    def add_arguments(self, parser):
        parser.add_argument("-f", "--flush", action="store_true", help="Flush Database Before Adding Database Entries")

    def handle(self, *args, **kwargs):
        flush = kwargs["flush"]

        youtube_api = YoutubeAPI(settings.YOUTUBE_API_KEY)
        hr_filter_titles = [code.label.lower() for code in self.filters.keys()]

        string_helper = StringHelper()

        competition_data = []

        self.stdout.write("Collecting Smite Competition Playlists")

        page_token = "BASE"
        while page_token != None:
            page_token = None if page_token == "BASE" else page_token

            api_parameters = {
                "part": "snippet",
                "channelId": settings.SMITE_VOD_ID,
                "pageToken": page_token,
                "maxResults": 50
            }

            playlist_batch = youtube_api.playlists(api_parameters)

            for playlist in playlist_batch["items"]:
                playlist_title = playlist["snippet"]["title"].lower()

                filter_check = string_helper.filter_string(
                        playlist_title,
                        string_helper.compound_filter(self.filters)
                    )

                if filter_check:
                    season_number = playlist_title.split("season")[-1]
                    league_index = hr_filter_titles.index(
                        list(
                            filter(lambda x: x in playlist_title, hr_filter_titles))[0])
                    league = list(self.filters.keys())[league_index]

                    competition_data.append({
                        "season": season_number,
                        "league": league,
                        "playlist_id": playlist["id"]
                    })

            if "nextPageToken" in playlist_batch:
                page_token = playlist_batch["nextPageToken"]
            else:
                break

        if flush:
            self.stdout.write("Flushing Competition Table")
            Match.objects.all().delete()

        self.stdout.write("Updating Database With Competitions")

        for data in competition_data:
            existing_comp = Competition.objects.filter(
                playlist_id=data["playlist_id"])

            if not existing_comp.exists():
                self.stdout.write(
                    "Adding {} {} To Database".format(data["league"], data["season"]))
                Competition(**data).save()
