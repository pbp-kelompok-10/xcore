from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Get your custom user model - this is IMPORTANT!
CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address."
    )
    profile_picture = forms.ImageField(
        required=False,
        help_text="Optional. Upload a profile picture."
    )

    class Meta:
        model = CustomUser  # This now points to your custom user model
        fields = ("username", "email", "password1", "password2", "profile_picture")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        # Handle profile picture
        if 'profile_picture' in self.files and self.files['profile_picture']:
            user.profile_picture = self.files['profile_picture']
        
        if commit:
            user.save()
        return user

@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({
            "status": False,
            "message": "Only POST requests are allowed."
        }, status=405)
    
    form = AuthenticationForm(request, data=request.POST)

    if form.is_valid():
        user = form.get_user()

        if user is not None and user.is_active:
            auth_login(request, user)
            return JsonResponse({
                "status": True,
                "username": user.username,
                "message": "Login successful!"
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Account is disabled."
            }, status=401)

    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed.",
            "errors": form.errors  
        }, status=401)

@csrf_exempt
@login_required
def logout(request):
    if request.method == "POST":
        auth_logout(request)
        return JsonResponse({
            "status": True,
            "message": "Logout successful!"
        }, status=200)
    else:
        return JsonResponse({
            "status": False,
            "message": "Only POST method allowed."
        }, status=405)

@csrf_exempt
def register_api(request):
    if request.method != "POST":
        return JsonResponse({
            "status": False,
            "message": "Only POST method allowed."
        }, status=405)
    
    form = CustomUserCreationForm(request.POST, request.FILES)

    if form.is_valid():
        user = form.save()

        return JsonResponse({
            "status": True,
            "message": "Account created successfully!",
            "username": user.username,
            "email": user.email,
        }, status=200)
    
    # Format errors properly for Flutter
    errors = {}
    for field, error_list in form.errors.items():
        errors[field] = [{"message": str(error)} for error in error_list]
    
    print(f"SERVER RESPONSE ERRORS: {errors}")

    return JsonResponse({
        "status": False,
        "message": "Registration failed.",
        "errors": errors
    }, status=400)