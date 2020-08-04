from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.core.paginator import Paginator

from .models import Highlight, Competition, Match
from .youtubeAPI import YoutubeAPI
# Create your views here.

class EsportsView(View):
    template_name = "esports/esports.html"

    def get(self, request):
        highlights = Highlight.objects.all().filter(disabled=False)

        spl_seasons = Competition.objects.all().filter(
            league=Competition.SMITE_PRO_LEAGUE)

        swc_seasons = Competition.objects.all().filter(
            league=Competition.SMITE_WORLD_CHAMPIONSHIP
        )

        context = {
            "highlights": highlights,
            "spl_years": spl_seasons,
            "swc_years": swc_seasons
        }

        return render(request, self.template_name, context)

class LeagueView(View):
    template_name = "esports/league.html"

    def get(self, request, competition_id, page_numb):
        chosen_competition = Competition.objects.get(id=competition_id)

        corresponding_matches = Match.objects.filter(
            competition=chosen_competition).order_by("-date_published")

        paginator = Paginator(corresponding_matches, 25)

        page = paginator.get_page(page_numb)

        context = {
            "id": chosen_competition.id,
            "league": chosen_competition.league,
            "season": chosen_competition.season,
            "page": page,
        }

        return render(request, "esports/league.html", context)

    def post(self, request, competition_id):
        post = request.POST["page-number"]
        return redirect(f"{competition_id}/{post}")

class MatchView(View):
    template_name = "esports/match.html"

    def get(self, request, match_id, video_numb=None):
        corresponding_match = Match.objects.get(id=match_id)
        if corresponding_match.multiple_parts() and video_numb is None:
            return redirect(f"{match_id}/1")
        elif corresponding_match.multiple_parts():
            video_in_parts = corresponding_match.ids.split(",")
            video_id = video_in_parts[video_numb - 1]
            start = video_id == video_in_parts[0]
            end = video_id == video_in_parts[-1]
        else:
            video_in_parts = []
            video_id = corresponding_match.ids
            start = None
            end = None

        context = {
            "id": video_id,
            "match-id": match_id,
            "parts": video_numb,
            "start": start,
            "end": end
        }

        return render(request, self.template_name, context)

class SearchView(View):
    template_name = "esports/search.html"

    def get(self, request, query, page_numb):
        string_query = query.replace("+", "")

        query_set = Match.objects.filter(title__contains=string_query).order_by("-date_published")

        paginator = Paginator(query_set, 25)

        page = paginator.get_page(page_numb)

        context = {
            "query": string_query,
            "page": page
        }

        return render(request, self.template_name, context)

    def post(self, request):
        query = request.POST["desired-search"]
        condensed_query = query.replace("+", " ")
        return redirect(f"{condensed_query}/1")




