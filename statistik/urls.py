from django.urls import path
from . import views
<<<<<<< HEAD
from highlights.views import highlight_detail
=======
>>>>>>> 05629e0 (statistik)

app_name = 'statistik'

urlpatterns = [
    path('', views.add_statistik, name='add_statistik'),  # Root langsung ke form add
    path('<int:match_id>/', views.statistik_display, name='statistik_display'),
<<<<<<< HEAD
    path('<uuid:match_id>/highlights/', highlight_detail, name='match_highlights'),
=======
>>>>>>> 05629e0 (statistik)
]