from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    profile_picture_url = None
    
    if user.profile_picture:
        profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'bio': user.bio,
        'profile_picture': profile_picture_url,
        'is_admin': user.is_admin,
    }, status=status.HTTP_200_OK)

