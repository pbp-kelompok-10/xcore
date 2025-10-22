from django.urls import path
from . import views

app_name = 'highlight'

urlpatterns = [
    path('match/<uuid:match_id>/highlights/', views.highlight_detail, name='match_highlights'),
    
    # Create operation
    path('match/<uuid:match_id>/highlights/create', views.highlight_create, name='highlight_create'),
    
    # Update operation
    path('match/<uuid:match_id>/highlights/update/', views.highlight_update, name='highlight_update'),
    
    # Delete operation
    path('match/<uuid:match_id>/highlights/delete/', views.highlight_delete, name='highlight_delete'),
]
