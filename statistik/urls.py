from django.urls import path
from . import views

app_name = 'statistik'

urlpatterns = [
    # Web views
    path('add/<uuid:match_id>/', views.add_statistik, name='add_statistik'),
    path('update/<uuid:match_id>/', views.update_statistik, name='update_statistik'),  
    path('delete/<uuid:match_id>/', views.delete_statistik, name='delete_statistik'),  
    path('<uuid:match_id>/', views.statistik_display, name='statistik_display'),
    
    # Legacy API endpoints
    path('<uuid:match_id>/json/', views.statistik_json, name='statistik_json'),
    path('json/', views.statistik_list_json, name='statistik_list_json'),
    
    # New Flutter API endpoints (Class-based views)
    path('flutter/<uuid:match_id>/', views.FlutterStatistikDetailView.as_view(), name='flutter_statistik_detail'),
    path('flutter/create/', views.FlutterStatistikCreateView.as_view(), name='flutter_statistik_create'),
    path('flutter/update/<uuid:match_id>/', views.FlutterStatistikUpdateView.as_view(), name='flutter_statistik_update'),
    path('flutter/delete/<uuid:match_id>/', views.FlutterStatistikDeleteView.as_view(), name='flutter_statistik_delete'),
    path('flutter/list/', views.FlutterStatistikListView.as_view(), name='flutter_statistik_list'),
    
    # User info endpoint
    path('user-info/', views.GetUserInfoView.as_view(), name='user_info'),
]