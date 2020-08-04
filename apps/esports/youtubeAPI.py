import json
from datetime import datetime

from googleapiclient import discovery
from googleapiclient import errors

class YoutubeAPI(object):

    request = None

    def __init__(self, api_key):
        self.youtube = discovery.build("youtube", "v3", developerKey=api_key)

    def playlists(self, parameters):
        check_params  = self.check_parameters(parameters)
        request = self.youtube.playlists().list(**check_params)
        return request.execute()

    def playlist_items(self, parameters):
        check_params  = self.check_parameters(parameters)
        request = self.youtube.playlistItems().list(**check_params)
        return request.execute()

    def channel_sections(self, parameters):
        check_params  = self.check_parameters(parameters)
        request = self.youtube.channelSections().list(**check_params)
        return request.execute()

    def search(self, parameters):
        check_params  =  self.check_parameters(parameters)
        request = self.youtube.search().list(**check_params)
        return request.execute()

    @staticmethod
    def check_parameters(parameters):
        if parameters:
            if "part" not in parameters:
                parameters["part"] = "snippet"
        else:
            raise ValueError("No Parameters Were Given To Search")

        return parameters

    @staticmethod
    def create_date_object(data_string):
        return datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def create_date_string(data_object):
        return datetime.strftime(data_object, "%Y-%m-%dT%H:%M:%SZ")
