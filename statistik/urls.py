from django.urls import path
from . import views

app_name = 'statistik'

urlpatterns = [
    path('add/<uuid:match_id>/', views.add_statistik, name='add_statistik'),
    path('update/<uuid:match_id>/', views.update_statistik, name='update_statistik'),  
    path('delete/<uuid:match_id>/', views.delete_statistik, name='delete_statistik'),  
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),
    # Tambahkan API endpoints untuk Flutter
    path('<uuid:match_id>/json/', views.statistik_json, name='statistik_json'),
    path('json/', views.statistik_list_json, name='statistik_list_json'),
     # NEW ENDPOINTS FOR FLUTTER CRUD
    path('create-flutter/', views.create_statistik_flutter, name='create_statistik_flutter'),
    path('update-flutter/<uuid:match_id>/', views.update_statistik_flutter, name='update_statistik_flutter'),
    path('delete-flutter/<uuid:match_id>/', views.delete_statistik_flutter, name='delete_statistik_flutter'),
]