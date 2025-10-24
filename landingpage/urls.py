from django.urls import path
from .views import landing_home, register, login_user, logout_user, profile_user

app_name = 'landingpage'


urlpatterns = [
    path('', landing_home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile_user, name='profile'),
]