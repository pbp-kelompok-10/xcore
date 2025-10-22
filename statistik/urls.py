from django.urls import path
from . import views

app_name = 'statistik'

urlpatterns = [
    path('', views.add_statistik, name='add_statistik'),
    path('add/<uuid:match_id>/', views.add_statistik_for_match, name='add_statistik_for_match'),  # TAMBAH INI
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),  # GANTI int jadi uuid
]