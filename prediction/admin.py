from django.contrib import admin
from .models import Prediction, Vote


# ==== 1️⃣ PREDICTION ADMIN ====
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'match', 'votes_home_team', 'votes_away_team', 'total_votes']
    search_fields = ['question', 'match__home_team', 'match__away_team']
    list_filter = ['match__status', 'match__match_date']
    readonly_fields = ['id', 'votes_home_team', 'votes_away_team', 'total_votes']

    fieldsets = (
        ('Match Information', {
            'fields': ('match', 'question')
        }),
        ('Team Logos', {
            'fields': ('logo_home_team', 'logo_away_team')
        }),
        ('Vote Statistics', {
            'fields': ('votes_home_team', 'votes_away_team', 'total_votes'),
            'classes': ('collapse',)
        }),
    )

    # Inline Vote objects directly under Prediction
    class VoteInline(admin.TabularInline):
        model = Vote
        extra = 0
        readonly_fields = ['user', 'choice', 'voted_at']
        can_delete = False

    inlines = [VoteInline]


# ==== 2️⃣ VOTE ADMIN ====
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prediction', 'choice', 'voted_at']
    search_fields = ['user__username', 'prediction__question', 'prediction__match__home_team']
    list_filter = ['choice', 'voted_at']
    readonly_fields = ['id', 'voted_at']
    ordering = ['-voted_at']
