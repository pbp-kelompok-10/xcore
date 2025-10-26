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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from scoreboard.models import Match
        self.fields['match'].queryset = Match.objects.filter(status__in=['live','finished'])
