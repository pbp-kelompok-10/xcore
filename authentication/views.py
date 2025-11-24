from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login as auth_login

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


from user.forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

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
    errors = {field: error.get_json_data() for field, error in form.errors.items()}
    print(f"SERVER RESPONSE: {errors}")

    return JsonResponse({
        "status": False,
        "message": "Registration failed.",
        "errors": errors
    }, status=400)


