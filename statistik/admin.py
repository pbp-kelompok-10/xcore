from django.contrib import admin
from .models import Statistik

@admin.register(Statistik)
class StatistikAdmin(admin.ModelAdmin):
    list_display = (
        'match',
        'shoot_home', 'shoot_away',
        'on_target_home', 'on_target_away',
        'ball_possession_home', 'ball_possession_away',
        'yellow_card_home', 'yellow_card_away',
        'red_card_home', 'red_card_away'
    )
    list_filter = ('match__status',)
    search_fields = (
        'match__home_team',
        'match__away_team',
        'match__stadium'
    )
    ordering = ('-match__match_date',)
    list_select_related = ('match',)

    fieldsets = (
        ('Match', {
            'fields': ('match',)
        }),
        ('Passing & Shooting', {
            'fields': (
                'pass_home', 'pass_away',
                'shoot_home', 'shoot_away',
                'on_target_home', 'on_target_away'
            )
        }),
        ('Ball Possession', {
            'fields': (
                'ball_possession_home', 'ball_possession_away'
            )
        }),
        ('Cards & Fouls', {
            'fields': (
                'yellow_card_home', 'yellow_card_away',
                'red_card_home', 'red_card_away'
            )
        }),
        ('Other Stats', {
            'fields': (
                'offside_home', 'offside_away',
                'corner_home', 'corner_away'
            )
        }),
    )

    def match_summary(self, obj):
        return f"{obj.match.home_team} vs {obj.match.away_team}"
    match_summary.short_description = "Match"

