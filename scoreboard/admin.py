from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team', 'away_team', 'home_score', 'away_score',
        'match_date', 'stadium', 'status', 'group', 'round'
    )
    list_filter = ('status', 'group', 'round', 'stadium')
    search_fields = ('home_team', 'away_team', 'stadium')
    ordering = ('-match_date',)
    readonly_fields = ('home_team', 'away_team', 'id')

    fieldsets = (
        ('Match Information', {
            'fields': (
                'id', 'match_date', 'stadium', 'status', 'group', 'round'
            )
        }),
        ('Teams', {
            'fields': (
                'home_team_code', 'away_team_code',
                'home_team', 'away_team'
            )
        }),
        ('Score', {
            'fields': ('home_score', 'away_score')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        qs = super().get_queryset(request)
        return qs.select_related()

    def match_summary(self, obj):
        return f"{obj.home_team} {obj.home_score} - {obj.away_score} {obj.away_team}"
    match_summary.short_description = "Result"

