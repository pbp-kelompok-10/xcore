from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'home_team',
            'away_team',
            'home_score',
            'away_score',
            'stadium',
            'round',
            'group',
            'status',
        ]
        widgets = {
            'status': forms.Select(choices=[
                ('upcoming', 'Upcoming'),
                ('live', 'Live'),
                ('finished', 'Finished'),
            ]),
        }
