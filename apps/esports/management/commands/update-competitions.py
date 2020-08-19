from django.core.management.base import BaseCommand

from esports.esportsdata import CompetitionData

class Command(BaseCommand):
    help = "Update The Exisiting Competition Data"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--flush", action="store_true", help="Flush Database Before Adding Database Entries")

    def handle(self, *args, **kwargs):
        flush = kwargs["flush"]

        competition_data = CompetitionData()
        competition_data.fetch_data()

        if flush:
            self.stdout.write("Flushing Competition Table")
            competition_data.flush_model()

        competition_data.commit_data()
