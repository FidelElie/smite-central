from datetime import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

# Create your models here.

class Competition(models.Model):
    SMITE_WORLD_CHAMPIONSHIP = "SWC"
    SMITE_PRO_LEAGUE = "SPL"

    SMITE_LEAGUES = [
        (SMITE_WORLD_CHAMPIONSHIP, "Smite World Championship"),
        (SMITE_PRO_LEAGUE, "Smite Pro League")
    ]

    league = models.CharField(
        max_length=3,
        choices=SMITE_LEAGUES,
        default=SMITE_PRO_LEAGUE
    )
    season = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])
    playlist_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.league} Season {self.season}"

class CompetitionMixin(object):
    def smite_league(self):
        if hasattr(self, "match"):
            return self.match.competition.league
        elif hasattr(self, "competition"):
            return self.competition.league

    def season_number(self):
        if hasattr(self, "match"):
            return self.match.competition.season
        elif hasattr(self, "competition"):
            return self.competition.season

class Match(models.Model, CompetitionMixin):
    title = models.CharField(max_length=200)
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE
    )
    ids = models.CharField(max_length=200)
    thumbnail = models.URLField()
    date_published = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

    def multiple_parts(self):
        return True if "," in self.ids else False

class Highlight(models.Model, CompetitionMixin):
    team_1 = models.CharField(max_length=30)
    team_2 = models.CharField(max_length=30)
    highlight_video_link = models.CharField(max_length=50)
    highlight_video = models.FileField(upload_to="videos/")
    disabled = models.BooleanField(default=False)
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        null=True
    )

    def is_disabled(self):
        return self.disabled

    def save(self, *args, **kwargs):
        highlight_video_id = self.highlight_video_link.split("v=")[-1]
        corresponding_match = Match.objects.get(ids__contains=highlight_video_id)
        self.match = corresponding_match
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.highlight_video.delete(save=False)
        super().delete(*args, **kwargs)


    def title(self):
        return self.__str__()

    def __str__(self):
        return f"{self.team_1} Vs {self.team_2}"


