# forms.py (di app yang sama dengan models)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    photo = forms.ImageField(required=False, label='Foto Profil')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'photo')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Buat atau update profil
            profile, created = Profile.objects.get_or_create(user=user)
            if self.cleaned_data.get('photo'):
                profile.photo = self.cleaned_data['photo']
                profile.save()
        return user
