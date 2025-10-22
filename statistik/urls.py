from django.urls import path
from . import views
from highlights.views import highlight_detail

app_name = 'statistik'

urlpatterns = [
    path('', views.add_statistik, name='add_statistik'),  # Root langsung ke form add
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),
    path('<uuid:match_id>/highlights/', highlight_detail, name='match_highlights'),
]