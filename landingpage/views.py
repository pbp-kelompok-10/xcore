from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import SignUpForm


# Create your views here.
def landing_home(request):
    context = {
        'title': 'Welcome to Xcore',
        'tagline': 'Web scoring terbaik cihuyyyyyyy',
        'features': [
            'Scoreboard',
            'Statistic', 
            'Highlight',
            'Prediction',
        ]
    }
    return render(request, 'landing.html', context)

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)  # ← penting: request.FILES
        if form.is_valid():
            form.save()  # otomatis buat user + profil + simpan foto
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun {username} berhasil dibuat! Silakan login.')
            return redirect('landingpage:login')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request): # ininya diganti apa
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('landingpage:home')

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('landingpage:home'))
    response.delete_cookie('last_login')
    return response

def profile_user(request):
    context = {
        'name': request.user.username,
    }
    return render(request, 'profile.html', context)
