from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ['home_team', 'away_team']
        widgets = {
            'match_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'id_match_date'}),
            'status': forms.Select(attrs={'class': 'form-control', 'id': 'id_status'}),
            'home_team_code': forms.Select(attrs={'class': 'form-control'}),
            'away_team_code': forms.Select(attrs={'class': 'form-control'}),
            'stadium': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama stadion...'}),
            'round': forms.NumberInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: A, B, C...'}),
            'home_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

