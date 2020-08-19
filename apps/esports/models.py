from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from django.core.validators import MinValueValidator

# Create your models here.

class League(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    tagline = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    competition_include_filters = ArrayField(
        models.CharField(max_length=100), blank=True)
    competition_exclude_filters = ArrayField(
        models.CharField(max_length=100), blank=True)
    match_include_filters = ArrayField(
        models.CharField(max_length=100), blank=True)
    match_exclude_filters = ArrayField(
        models.CharField(max_length=100), blank=True)

    def save(self, *args, **kwargs):
        split_title = self.title.split(" ")
        code_title = [word[0].upper() for word in split_title]
        self.code = "".join(code_title)
        super().save(*args, **kwargs)

class Competition(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE
    )
    season = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])
    playlist_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.league.title} Season {self.season}"

class Match(models.Model):
    title = models.CharField(max_length=200)
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE
    )
    ids = ArrayField(models.CharField(max_length=25))
    thumbnail = models.URLField()
    date_published = models.DateTimeField(null=True)

    def multiple_parts(self):
        return len(self.ids) > 1

    def season_number(self):
        return self.competition.season

    def league_title(self):
        return self.competition.league.title

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
