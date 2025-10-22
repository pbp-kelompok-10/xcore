from django import forms
from embed_video.fields import EmbedVideoField
from .models import Highlight

class HighlightForm(forms.ModelForm):
    class Meta:
        model = Highlight
        fields = ['video']
        widgets = {
            'video': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paste YouTube/Vimeo embed URL here',
            }),
        }

class HighlightCreateForm(forms.ModelForm):
    class Meta:
        model = Highlight
        fields = ['match', 'video']
        widgets = {
            'match': forms.Select(attrs={
                'class': 'form-control',
            }),
            'video': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paste YouTube/Vimeo embed URL here',
            }),
        }
