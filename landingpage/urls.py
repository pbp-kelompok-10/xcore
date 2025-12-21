from django.urls import path
from .views import landing_home, register, login_user, logout_user, profile, show_profile_json, update_profile_flutter

app_name = 'landingpage'

urlpatterns = [
    path('', landing_home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    # --- ENDPOINT KHUSUS FLUTTER ---
    path('profile/json/', show_profile_json, name='show_profile_json'),
    path('profile/update-flutter/', update_profile_flutter, name='update_profile_flutter'),
]
