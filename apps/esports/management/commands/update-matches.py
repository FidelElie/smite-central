from django.core.management.base import BaseCommand

from esports.esportsdata import MatchData

class Command(BaseCommand):
    help = "Update The Existing Matches Data"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--flush", action="store_true", help="Flush Database Before Adding Database Entries")

    def handle(self, *args, **kwargs):
        flush = kwargs["flush"]

        match_data = MatchData()
        match_data.fetch_data()

        if flush:
            self.stdout.write("Flushing Matches Table")
            match_data.flush_model()

        match_data.commit_data()
