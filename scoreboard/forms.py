from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ['home_team', 'away_team']
        widgets = {
            'match_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'home_team_code': forms.Select(attrs={'class': 'form-control'}),
            'away_team_code': forms.Select(attrs={'class': 'form-control'}),
            'stadium': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama stadion...'}),
            'round': forms.NumberInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: A, B, C...'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'home_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['home_team_code'].label = "Tuan Rumah (Kode Negara)"
        self.fields['away_team_code'].label = "Tamu (Kode Negara)"
        self.fields['match_date'].label = "Tanggal Pertandingan"
        self.fields['stadium'].label = "Stadion"
        self.fields['round'].label = "Round"
        self.fields['group'].label = "Group"
        self.fields['status'].label = "Status"
