from django.core.management.base import BaseCommand, CommandError

from esports.models import League, Competition, Match, Image

class Command(BaseCommand):
    league_strings = ["league", "leagues"]
    competition_strings = ["competition", "competitions"]
    match_strings = ["match", "matches"]
    image_strings = ["image", "images"]


    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Indicates What Model To Flush")

    def handle(self, *args, **kwargs):
        chosen_model = kwargs["model"]

        if chosen_model.lower() in self.league_strings:
            League.objects.all().delete()
        elif chosen_model.lower() in self.competition_strings:
            Competition.objects.all().delete()
        elif chosen_model.lower() in self.match_strings:
            Match.objects.all().delete()
        elif chosen_model.lower() in self.image_strings:
            Image.objects.all().delete()
        else:
            raise CommandError("Invalid Model Provided")

        self.stdout.write(f"Entries Flushed For Model: {chosen_model}")
