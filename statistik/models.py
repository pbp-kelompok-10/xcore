from django.db import models

class Statistik(models.Model):
    # GANTI: match_id jadi ForeignKey ke Match
    match = models.ForeignKey(
        'scoreboard.Match',
        on_delete=models.CASCADE,
        related_name='statistics'
    )
    
    # HAPUS field duplikat ini:
    # - team_home, team_away, score_home, score_away, stadium
    
    # SIMPAN hanya field statistik:
    pass_home = models.IntegerField(default=0)
    pass_away = models.IntegerField(default=0)
    shoot_home = models.IntegerField(default=0)
    shoot_away = models.IntegerField(default=0)
    on_target_home = models.IntegerField(default=0)
    on_target_away = models.IntegerField(default=0)
    ball_possession_home = models.FloatField(default=0)
    ball_possession_away = models.FloatField(default=0)
    red_card_home = models.IntegerField(default=0)
    red_card_away = models.IntegerField(default=0)
    yellow_card_home = models.IntegerField(default=0)
    yellow_card_away = models.IntegerField(default=0)
    offside_home = models.IntegerField(default=0)
    offside_away = models.IntegerField(default=0)
    corner_home = models.IntegerField(default=0)
    corner_away = models.IntegerField(default=0)

    def __str__(self):
        return f"Statistik for {self.match.home_team} vs {self.match.away_team}"