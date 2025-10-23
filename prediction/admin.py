from django.contrib import admin
from .models import Match, Prediction, Vote


# ==== 1️⃣ MATCH ADMIN ====
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team', 'away_team', 'match_date', 'stadium',
        'status', 'home_score', 'away_score'
    )
    list_filter = ('status', 'match_date', 'stadium')
    search_fields = ('home_team', 'away_team', 'stadium')
    ordering = ('-match_date',)
    readonly_fields = ('id',)
    fieldsets = (
        ('Teams', {
            'fields': ('home_team', 'home_team_code', 'away_team', 'away_team_code')
        }),
        ('Match Details', {
            'fields': ('match_date', 'stadium', 'round', 'group', 'status')
        }),
        ('Score', {
            'fields': ('home_score', 'away_score')
        }),
    )

    # Inline Prediction biar keliatan langsung di bawah Match
    class PredictionInline(admin.StackedInline):
        model = Prediction
        extra = 0
        readonly_fields = ('id', 'votes_home_team', 'votes_away_team', 'total_votes')
        can_delete = False

    inlines = [PredictionInline]


# ==== 2️⃣ PREDICTION ADMIN ====
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'match', 'votes_home_team', 'votes_away_team', 'total_votes']
    search_fields = ['question', 'match__home_team', 'match__away_team']
    list_filter = ['match__status', 'match__match_date']
    readonly_fields = ['id', 'votes_home_team', 'votes_away_team']

    fieldsets = (
        ('Match Information', {
            'fields': ('match', 'question')
        }),
        ('Team Logos', {
            'fields': ('logo_home_team', 'logo_away_team')
        }),
        ('Vote Statistics', {
            'fields': ('votes_home_team', 'votes_away_team'),
            'classes': ('collapse',)
        }),
    )

    class VoteInline(admin.TabularInline):
        model = Vote
        extra = 0
        readonly_fields = ['user', 'choice', 'voted_at']
        can_delete = False

    inlines = [VoteInline]


# ==== 3️⃣ VOTE ADMIN ====
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prediction', 'choice', 'voted_at']
    search_fields = ['user__username', 'prediction__question']
    list_filter = ['choice', 'voted_at']
    readonly_fields = ['id', 'voted_at']
