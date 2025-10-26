from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login,logout
from user.forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from user.forms import EditProfileForm
# Create your views here.
def landing_home(request):
    context = {
        'title': 'Welcome to Xcore',
        'tagline': 'Your Ultimate Football Companion',
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
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been successfully created!")
            return redirect('landingpage:login')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('scoreboard:scoreboard_list')

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('landingpage:home'))
    response.delete_cookie('last_login')
    messages.success(request, "You have successfully logged out.")
    return response

@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('landingpage:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EditProfileForm(instance=user)

    context = {
        'form': form,
        'user': user
    }
    return render(request, 'profile.html', context)
