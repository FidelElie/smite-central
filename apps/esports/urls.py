from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.EsportsView.as_view(), name="esports"),

    path("league/<int:league_id>", views.LeagueView.as_view(), name="league"),
    path("league/<int:league_id>/<int:competition_id>", views.LeagueView.as_view(), name="league"),

    path("season/<int:competition_id>", views.SeasonView.as_view(), name="season"),
    path("season/<int:competition_id>/<int:page_numb>", views.SeasonView.as_view(), name="season"),

    path("video/<int:match_id>", views.MatchView.as_view(), name="match"),
    path("video/<int:match_id>/<int:video_numb>", views.MatchView.as_view(), name="match"),

    path("search/", views.SearchView.as_view(), name="search"),
    path("search/<query>/<int:page_numb>", views.SearchView.as_view(), name="search")
]
