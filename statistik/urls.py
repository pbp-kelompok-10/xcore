from django.urls import path
from . import views

app_name = 'statistik'

urlpatterns = [
    path('add/<uuid:match_id>/', views.add_statistik, name='add_statistik'),
    path('update/<uuid:match_id>/', views.update_statistik, name='update_statistik'),  
    path('delete/<uuid:match_id>/', views.delete_statistik, name='delete_statistik'),  
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),
]