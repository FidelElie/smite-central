from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.core.paginator import Paginator

from .models import League, Competition, Match, Image
# Create your views here.

class EsportsView(View):
    template_name = "esports/esports.html"

    def get(self, request):
        images = Image.objects.all().filter(disabled=False).order_by("id")

        league_entries = list(League.objects.all().order_by("id"))
        comp_entries = list(Competition.objects.all().order_by("-season").prefetch_related("league"))

        esports_info = []

        for entry in league_entries:
            league_code = entry.code.lower()
            league_tagline = entry.tagline
            league_logo = "esports/images/{}.png".format(league_code)
            seasons = [e for e in comp_entries if e.league == entry]

            esports_info.append(
                {
                    "league": entry,
                    "logo": league_logo,
                    "seasons": seasons
                }
            )

        context = {
            "images": images,
            "esports_info": esports_info,
            "channel_id": settings.SMITE_VOD_ID
        }

        return render(request, self.template_name, context)

class LeagueView(View):
    template_name = "esports/league.html"

    def get(self, request, league_id, competition_id=None):
        league = League.objects.get(id=league_id)
        competitions = Competition.objects.filter(league=league).order_by("-season")

        if competition_id == None:
            return redirect("league", league_id=league_id, competition_id=competitions[0].id)

        current_competition = competitions.get(id=competition_id)
        corresponding_matches = Match.objects.filter(
            competition=current_competition).order_by("-date_published")

        paginator = Paginator(corresponding_matches, 6, orphans=5)

        page = paginator.get_page(1)

        context = {
            "league": league,
            "competitions": competitions,
            "current_comp": current_competition,
            "page": page,
            "logo": "esports/images/{}.png".format(league.code.lower())
        }

        return render(request, self.template_name, context)

    def post(self, request, league_id, competition_id):
        post = request.POST["page-number"]
        return redirect(f"{competition_id}/{post}")

class SeasonView(View):
    template_name = "esports/season.html"

    def get(self, request, competition_id, page_numb):
        chosen_competition = Competition.objects.get(id=competition_id)

        corresponding_matches = Match.objects.filter(
            competition=chosen_competition).order_by("-date_published")

        paginator = Paginator(corresponding_matches, 25)

        page = paginator.get_page(page_numb)

        context = {
            "id": chosen_competition.id,
            "league": chosen_competition.league.code,
            "season": chosen_competition.season,
            "page": page,
        }

        return render(request, self.template_name, context)

    def post(self, request, competition_id):
        post = request.POST["page-number"]
        return redirect(f"{competition_id}/{post}")

class MatchView(View):
    template_name = "esports/match.html"

    def get(self, request, match_id, video_numb=None):
        corresponding_match = Match.objects.get(id=match_id)
        if corresponding_match.multiple_parts() and video_numb is None:
            return redirect("match", match_id=match_id, video_numb=1)
        elif corresponding_match.multiple_parts():
            video_id = corresponding_match.ids[video_numb - 1]
            start = video_id == corresponding_match.ids[0]
            end = video_id == corresponding_match.ids[-1]
        else:
            video_in_parts = []
            video_id = corresponding_match.ids[0]
            start = None
            end = None

        context = {
            "id": video_id,
            "title": corresponding_match.title,
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

        query_set = Match.objects.filter(title__icontains=string_query).order_by("-date_published")

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
        return redirect("search", query=condensed_query, page_numb=1)




