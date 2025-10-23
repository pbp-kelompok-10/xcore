from django.db import models
from scoreboard.models import Match

class Statistik(models.Model):
    # Field yang sudah ada
    match = models.ForeignKey(Match, on_delete=models.CASCADE)  
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

    # Field baru dengan default
    team_home = models.CharField(max_length=100, default='Team Home')
    team_away = models.CharField(max_length=100, default='Team Away')
    score_home = models.IntegerField(default=0)
    score_away = models.IntegerField(default=0)
    stadium = models.CharField(max_length=100, default='Stadium')

    # Property methods dengan error handling
    @property
    def pass_home_percentage(self):
        try:
            total = self.pass_home + self.pass_away
            return round((self.pass_home / total * 100) if total > 0 else 50, 1)
        except:
            return 50

    @property
    def shoot_home_percentage(self):
        try:
            total = self.shoot_home + self.shoot_away
            return round((self.shoot_home / total * 100) if total > 0 else 50, 1)
        except:
            return 50

    @property
    def on_target_home_percentage(self):
        try:
            total = self.on_target_home + self.on_target_away
            return round((self.on_target_home / total * 100) if total > 0 else 50, 1)
        except:
            return 50

    def __str__(self):
        return f"{self.team_home} vs {self.team_away}"