import uuid
from django.db import models
from django.contrib.auth.models import User
from scoreboard.models import Match

class Forum(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    
    def __str__(self):
        return self.id + "-" + self.forum.id
