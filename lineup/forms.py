from django import forms
from .models import Lineup,Player,Team
from django.forms import inlineformset_factory

class LineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ['match']  

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['code'] 

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['nama', 'asal', 'umur', 'nomor']

PlayerInlineFormSet = inlineformset_factory(
    Team,
    Player,
    form=PlayerForm,
    fields=['nama', 'asal', 'umur', 'nomor'],
    extra=1,            
    can_delete=True     
)

