from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
# Tambahkan di imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

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
                "user_id" : user.id,
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
def logout(request):  # HAPUS @login_required
    """
    Custom logout view that returns JSON
    """
    if request.method == "POST":
        print("🔄 Processing logout request...")
        
        # Check if user is actually logged in
        if request.user.is_authenticated:
            username = request.user.username
            auth_logout(request)
            print(f"✅ User {username} logged out successfully")
            
            return JsonResponse({
                "status": True,
                "message": "Logout successful!",
                "username": username
            }, status=200)
        else:
            # User already logged out or not authenticated
            print("ℹ️ User was not logged in")
            return JsonResponse({
                "status": True,
                "message": "User was not logged in."
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


# Tambahkan setelah fungsi yang ada
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """
    Get current user information including admin status
    """
    user = request.user
    return JsonResponse({
        "status": True,
        "user": {
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_admin": user.is_staff or user.is_superuser
        }
    })

@csrf_exempt
def login_with_token(request):
    """
    Modified login that returns token for Flutter
    """
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
            
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            return JsonResponse({
                "status": True,
                "username": user.username,
                "token": token.key,
                "user_info": {
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_admin": user.is_staff or user.is_superuser
                },
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