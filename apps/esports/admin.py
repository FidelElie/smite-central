from django.contrib import admin

from .models import Competition, Match, Image

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "competition_league", "season_number"]

class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "__str__", "competition_league", "season_number", "multiple_parts", "get_date_published"]

class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "__str__", "is_disabled"]

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

admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Image, ImageAdmin)
