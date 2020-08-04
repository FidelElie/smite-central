from django.core.management.base import BaseCommand, CommandError
from django.contrib import admin
from django.conf import settings

from esports.models import Competition
from esports.youtubeAPI import YoutubeAPI

class Command(BaseCommand):
    help = "Update The Exisiting Command Data"

    def handle(self, *args, **kwargs):
        youtube_api = YoutubeAPI(settings.YOUTUBE_API_KEY)

        api_parameters = {
            "part": "snippet ,contentDetails",
            "channelId": settings.SMITE_VOD_ID,
        }

        channel_sections = youtube_api.channel_sections(api_parameters)

        for item in channel_sections["items"]:
            if "title" in item["snippet"]:
                snippet_title = item["snippet"]["title"].lower()
                if snippet_title == "smite world championships":
                    swc_playlists = item["contentDetails"]["playlists"]
                elif snippet_title == "smite pro league - archive":
                    spl_playlists = item["contentDetails"]["playlists"]

        api_parameters = {
            "part": "snippet",
            "maxResults": 50,
            "id": swc_playlists + spl_playlists
        }

        playlist_items = youtube_api.playlists(api_parameters)

        Competition.objects.all().delete()

        for playlist in playlist_items["items"]:
            playlist_title = playlist["snippet"]["title"].lower()
            if "smite pro league" in playlist_title:
                comp_entry = self.create_comp_object(
                    playlist, Competition.SMITE_PRO_LEAGUE)
                comp_entry.save()
            elif "smite world championship" in playlist_title:
                comp_entry = self.create_comp_object(
                    playlist, Competition.SMITE_WORLD_CHAMPIONSHIP)
                comp_entry.save()

    @staticmethod
    def create_comp_object(playlist_data, comp_league):
        season_number = playlist_data["snippet"]["title"].lower().split("season")[-1]
        return Competition(
            league = comp_league,
            season = season_number,
            playlist_id = playlist_data["id"]
        )
