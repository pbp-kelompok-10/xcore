from django.contrib import admin
from .models import Team, Player, Lineup

# --- PLAYER INLINE ---
class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1
    fields = ('nama', 'asal', 'umur', 'nomor')
    ordering = ['nomor']

# --- TEAM ADMIN ---
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'player_count')
    search_fields = ('name', 'code')
    ordering = ('name',)
    inlines = [PlayerInline]

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Number of Players"


# --- PLAYER ADMIN ---
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nomor', 'tim', 'umur', 'asal')
    search_fields = ('nama', 'tim__name', 'asal')
    list_filter = ('tim',)
    ordering = ('tim', 'nomor')


# --- LINEUP ADMIN ---
@admin.register(Lineup)
class LineupAdmin(admin.ModelAdmin):
    list_display = ('match', 'team', 'player_list')
    search_fields = ('match__home_team', 'match__away_team', 'team__name')
    list_filter = ('team', 'match__status')
    ordering = ('match__match_date',)

    def player_list(self, obj):
        """Show a short comma-separated list of players."""
        players = obj.players.all().order_by('nomor')
        if not players:
            return "—"
        return ", ".join([f"{p.nama} (#{p.nomor})" for p in players[:5]]) + (
            "..." if players.count() > 5 else ""
        )
    player_list.short_description = "Players"
