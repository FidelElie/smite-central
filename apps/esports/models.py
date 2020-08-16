import os

from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class CompMixin(object):
    def season_number(self):
        if hasattr(self, "competition"):
            return self.competition.season
        else:
            return self.season

    def competition_league(self):
        if hasattr(self, "competition"):
            return self.competition.league
        else:
            return self.league

class Competition(models.Model, CompMixin):
    class CompetitionLeagues(models.TextChoices):
        SMITE_PRO_LEAGUE = "SPL", "Smite Pro League"
        SMITE_WORLD_CHAMPIONSHIP = "SWC", "Smite World Championship"
        SMITE_CHALLENGER_CIRCUIT = "SCC", "Smite Challenger Circuit"
        SMITE_OPEN_CIRCUIT = "SOC", "Smite Open Circuit"

    league = models.CharField(
        max_length=3,
        choices=CompetitionLeagues.choices,
        default=CompetitionLeagues.SMITE_PRO_LEAGUE
    )
    season = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])
    playlist_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.league} Season {self.season}"

class Match(models.Model, CompMixin):
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

    def get_date_published(self):
        return self.date_published

class Image(models.Model):
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to="esports/images")
    disabled = models.BooleanField(default=False)

    _original_image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._original_image is not None:
            self._original_image.delete(save=False)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def is_disabled(self):
        return self.disabled

    def __str__(self):
        return self.title
