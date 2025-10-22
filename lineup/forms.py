from django import forms
from .models import Lineup

class LineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ['match']  # Only the match field now
