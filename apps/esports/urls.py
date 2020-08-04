from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.EsportsView.as_view(), name="esports"),

    path("league/<int:competition_id>", views.LeagueView.as_view(), name="league"),
    path("league/<int:competition_id>/<int:page_numb>", views.LeagueView.as_view(), name="league"),

    path("video/<int:match_id>", views.MatchView.as_view(), name="match"),
    path("video/<int:match_id>/<int:video_numb>", views.MatchView.as_view(), name="match"),

    path("search/", views.SearchView.as_view(), name="search"),
    path("search/<query>/<int:page_numb>", views.SearchView.as_view(), name="search")
]
