from django.urls import path
from prediction.views import show_main

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
]

