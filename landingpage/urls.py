from django.urls import path
<<<<<<< HEAD
from .views import landing_home, register, login_user, logout_user, profile_user
=======
from .views import landing_home, register, login_user, logout_user, profile
>>>>>>> 523d9202db6f4faa050244adf309e4b939a66267

app_name = 'landingpage'

urlpatterns = [
    path('', landing_home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
<<<<<<< HEAD
    path('profile/', profile_user, name='profile'),
]
=======
    path('profile/', profile, name='profile'),
]
>>>>>>> 523d9202db6f4faa050244adf309e4b939a66267
