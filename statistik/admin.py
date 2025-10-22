from django.contrib import admin
from .models import Statistik

@admin.register(Statistik)
class StatistikAdmin(admin.ModelAdmin):
    list_display = ['id', 'match_id', 'shoot_home', 'shoot_away', 'ball_possession_home', 'ball_possession_away']
