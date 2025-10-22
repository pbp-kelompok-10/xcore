from django.urls import path
from . import views

app_name = 'statistik'

urlpatterns = [
    path('add/<uuid:match_id>/', views.add_statistik, name='add_statistik'),
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),
]