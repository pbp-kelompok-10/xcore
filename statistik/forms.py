from django import forms
from .models import Statistik

class StatistikForm(forms.ModelForm):
    class Meta:
        model = Statistik
        fields = [
            'match', 
            'pass_home', 'pass_away', 'shoot_home', 'shoot_away', 
            'on_target_home', 'on_target_away', 'ball_possession_home', 
            'ball_possession_away', 'red_card_home', 'red_card_away',
            'yellow_card_home', 'yellow_card_away', 'offside_home', 
            'offside_away', 'corner_home', 'corner_away'
        ]
        widgets = {
            'match': forms.HiddenInput(),  
        }
    
    def clean(self):
        cleaned_data = super().clean()
        match = cleaned_data.get('match')
        
        # Validasi: hanya match dengan status live atau finished yang boleh punya statistik
        if match and match.status not in ['live', 'finished']:
            raise forms.ValidationError(
                f"Tidak bisa menambah statistik untuk pertandingan dengan status: {match.status}. "
                "Hanya pertandingan live atau finished yang bisa memiliki statistik."
            )
        
        return cleaned_data