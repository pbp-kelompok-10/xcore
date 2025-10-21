from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'match_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'home_team_code': forms.Select(attrs={'class': 'form-control'}),
            'away_team_code': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stadium'].widget.attrs.update({'placeholder': 'Nama stadion...'})
