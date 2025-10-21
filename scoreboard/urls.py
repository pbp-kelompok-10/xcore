from django.urls import path
from . import views

urlpatterns = [
    path('', views.scoreboard_list, name='scoreboard_list'),
]
