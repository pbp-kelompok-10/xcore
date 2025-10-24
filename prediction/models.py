import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from scoreboard.models import Match
import uuid
from django.conf import settings

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
        return self.votes_home_team + self.votes_away_team

    @property
    def home_percentage(self):
        total = self.total_votes
        return (self.votes_home_team / total * 100) if total > 0 else 0

    @property
    def away_percentage(self):
        total = self.total_votes
        return (self.votes_away_team / total * 100) if total > 0 else 0
    
    def is_voting_open(self):
        """Check apakah voting masih bisa dilakukan"""
        now = timezone.now()
        match_time = self.match.match_date 
        deadline = match_time - timezone.timedelta(hours=2)
        return now < deadline


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='votes')
    choice = models.CharField(max_length=100) 
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prediction')

    def __str__(self):
        return f"{self.user.username} voted {self.choice}"

    def can_modify(self):
        """Check apakah vote masih bisa diubah/dihapus (sebelum deadline)"""
        return self.prediction.is_voting_open()
