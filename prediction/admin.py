from django.contrib import admin
from .models import Prediction, Vote

# Register your models here.

# Register Prediction ke Django Admin
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    # Kolom yang ditampilin di list
    list_display = ['id', 'question', 'match', 'votes_home_team', 'votes_away_team', 'total_votes']
    
    # Kolom yang bisa di-search
    search_fields = ['question', 'match__home_team', 'match__away_team']
    
    # Filter sidebar
    list_filter = ['match__status', 'match__match_date']
    
    # Kolom yang read-only (ga bisa diedit)
    readonly_fields = ['id', 'votes_home_team', 'votes_away_team']
    
    # Fieldset (grouping fields di form)
    fieldsets = (
        ('Match Information', {
            'fields': ('match', 'question')
        }),
        ('Team Logos', {
            'fields': ('logo_home_team', 'logo_away_team')
        }),
        ('Vote Statistics', {
            'fields': ('votes_home_team', 'votes_away_team'),
            'classes': ('collapse',)  # bisa di-collapse
        }),
    )
    
    # Inline untuk menampilkan related votes
    class VoteInline(admin.TabularInline):
        model = Vote
        extra = 0
        readonly_fields = ['user', 'choice', 'voted_at']
        can_delete = False
    
    inlines = [VoteInline]


# Register Vote ke Django Admin
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prediction', 'choice', 'voted_at']
    search_fields = ['user__username', 'prediction__question']
    list_filter = ['choice', 'voted_at']
    readonly_fields = ['id', 'voted_at']