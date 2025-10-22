from django.urls import path
from . import views

app_name = 'landingpage'


urlpatterns = [
    path('', views.landing_home, name='home'),
    path('register/', views.register, name='register'),
]