from django import forms
from .models import Lineup,Player,Team
from django.forms import inlineformset_factory

class LineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ['match']  # Only the match field now

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['code']  # name auto-updates from code

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['nama', 'asal', 'umur', 'nomor']

# Inline formset for managing players under a team
PlayerInlineFormSet = inlineformset_factory(
    Team,
    Player,
    form=PlayerForm,
    fields=['nama', 'asal', 'umur', 'nomor'],
    extra=1,             # 1 empty form to add a new player
    can_delete=True      # allow deleting existing players
)

