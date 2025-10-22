
import uuid
from django.db import models
from django.contrib.auth.models import User
from scoreboard.models import Match

# Create your models here.

# menyimpan Prediction/voting untuk setiap pertandingan
class Prediction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='prediction')
    votes_home_team = models.IntegerField(default=0)
    votes_away_team = models.IntegerField(default=0)
    logo_home_team = models.URLField(blank=True, null=True)
    logo_away_team = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Prediction for {self.match}"

    @property
    def total_votes(self):
        return self.votes_team_home + self.votes_team_away

    @property
    def home_percentage(self):
        total = self.total_votes
        return (self.votes_team_home / total * 100) if total > 0 else 0

    @property
    def away_percentage(self):
        total = self.total_votes
        return (self.votes_team_away / total * 100) if total > 0 else 0

# menyimpan vote user untuk setiap Prediction
class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='votes')
    choice = models.CharField(max_length=100) 
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prediction')  # biar 1 user cuma bisa vote 1 kali per prediction

    def __str__(self):
        return f"{self.user.username} voted {self.choice} on '{self.prediction.question}'"
