from django.db import models
import uuid

# Create your models here.
class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    match_date = models.DateTimeField()
    stadium = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=[
            ('upcoming', 'Upcoming'),
            ('live', 'Live'),
            ('finished', 'Finished'),
        ],
        default='upcoming'
    )

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"