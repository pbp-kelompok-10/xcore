
import uuid
from django.db import models
from django.contrib.auth.models import User
from scoreboard.models import Match

# Create your models here.

# Untuk menyimpan polling/voting pada setiap pertandingan
class Polling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='polling')
    votes_team_home = models.IntegerField(default=0)
    votes_team_away = models.IntegerField(default=0)

    def __str__(self):
        return f"Polling for {self.match}"

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


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    
    polling = models.ForeignKey(Polling, on_delete=models.CASCADE, related_name='votes')
    choice = models.CharField(max_length=100) 
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'polling')  # biar 1 user cuma bisa vote 1 kali per polling

    def __str__(self):
        return f"{self.user.username} voted {self.choice} on '{self.polling.question}'"
