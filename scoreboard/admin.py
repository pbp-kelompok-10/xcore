from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'home_score', 'away_score', 'match_date', 'status']
    list_filter = ['status', 'match_date']
    search_fields = ['home_team', 'away_team']
    readonly_fields = ['home_team', 'away_team']
