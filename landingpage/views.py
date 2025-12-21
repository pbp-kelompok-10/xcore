from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from user.forms import CustomUserCreationForm, EditProfileForm
import base64
from django.core.files.base import ContentFile

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

@login_required
def show_profile_json(request):
    user = request.user
    
    # Handle URL gambar profile
    profile_picture_url = None
    if user.profile_picture and hasattr(user.profile_picture, 'url'):
        profile_picture_url = user.profile_picture.url

    return JsonResponse({
        "username": user.username,
        "email": user.email,
        # Pastikan field 'bio' ada di model User kamu. Kalau error, ganti user.bio jadi ""
        "bio": getattr(user, 'bio', ""), 
        "profile_picture": profile_picture_url,
    })

@csrf_exempt
def update_profile_flutter(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

    try:
        user = request.user
        
        # 1. Update Text Data (Sama kayak sebelumnya)
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.bio = request.POST.get("bio", getattr(user, 'bio', ""))

        # 2. Update File Gambar dari Base64 (LOGIKA BARU)
        image_data = request.POST.get("image") # Kita ambil string base64
        image_name = request.POST.get("image_name") # Nama filenya

        if image_data and image_name:
            # Decode string base64 kembali menjadi file gambar
            format, imgstr = image_data.split(';base64,') if ";base64," in image_data else (None, image_data)
            ext = format.split('/')[-1] if format else "jpg"
            
            data = ContentFile(base64.b64decode(imgstr), name=image_name)
            user.profile_picture = data

        # 3. Save
        user.save()

        return JsonResponse({
            "status": "success",
            "message": "Profile updated successfully!",
            "username": user.username,
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)