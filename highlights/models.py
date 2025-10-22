from django.db import models
from embed_video.fields import EmbedVideoField
from scoreboard.models import Match


class Highlight(models.Model):
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name='highlight'
    )
    # use EmbedVideoField instead of URLField
    video = EmbedVideoField(help_text="YouTube, Vimeo, or other embed link", blank=True, null=True)

    def __str__(self):
        return f"Highlight for {self.match}"
