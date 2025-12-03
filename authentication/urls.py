from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register_api, name='register_api'),
    
    # NEW ENDPOINTS
    path('login-token/', views.login_with_token, name='login_token'),
    path('user-info/', views.get_user_info, name='user_info'),
    
    # status admin
    path('is-admin/', views.status_admin, name='is_admin'),
]