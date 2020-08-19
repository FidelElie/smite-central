from django.contrib import admin
from django.db import models
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from .models import League, Competition, Match, Image

class LeagueAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ["title", "code", "tagline"]
    readonly_fields = ["code"]
    fieldsets = (
        ("Information",
        {"fields": (
            "title", "code", "tagline", "description")}),
        ("Competition",
        {"fields": (
            "competition_include_filters", "competition_exclude_filters")}),
        ("Match",
        {"fields": (
            "match_include_filters", "match_exclude_filters"
        )})
    )

class MatchAdmin(admin.ModelAdmin):
    list_display = ["title", "league_title", "season_number", "multiple_parts", "date_published"]
    readonly_fields = ["ids"]
    list_filter = ["competition", "date_published"]
    search_fields = ["title"]

class ImageAdmin(admin.ModelAdmin):
    list_display = ["title", "disabled"]

    actions = ["remove_selected", "toggle_disable"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def remove_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

    def toggle_disable(self, request, queryset):
        for obj in queryset:
            obj.disabled = not obj.disabled
            obj.save()

admin.site.register(League, LeagueAdmin)
admin.site.register(Competition)
admin.site.register(Match, MatchAdmin)
admin.site.register(Image, ImageAdmin)
