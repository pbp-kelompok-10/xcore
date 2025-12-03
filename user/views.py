from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def create_admin_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("user:create-admin")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("user:create-admin")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_admin=True, 
        )

        messages.success(request, f"✅ Admin user '{username}' created successfully.")
        return redirect("landingpage:home")

    return render(request, "create_admin.html")
