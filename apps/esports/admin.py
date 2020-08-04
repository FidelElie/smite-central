from django.contrib import admin

from .models import Highlight, Competition, Match

class HighlightAdmin(admin.ModelAdmin):
    actions = ["remove_selected", "toggle_disable"]

    list_display = ["__str__", "smite_league", "season_number", "is_disabled"]

    fieldsets = [
        ("Highlight Teams", {"fields": ["team_1", "team_2"]}),
        ("Video Information", {"fields": ["highlight_video_link", "highlight_video"]}),
        ("Advanced", {"fields": ["disabled", "match"]})
    ]

    readonly_fields = ["match"]

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


class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "__str__", "smite_league", "season_number", "multiple_parts"]

admin.site.register(Highlight, HighlightAdmin)
admin.site.register(Competition)
admin.site.register(Match, MatchAdmin)

