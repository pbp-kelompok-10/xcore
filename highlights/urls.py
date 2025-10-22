from django.urls import path
from . import views

urlpatterns = [
    # Read operations
    path('highlights/test/', views.highlight_test, name='highlight_test'),
    path('highlights/test/create/', views.highlight_test_create_form, name='highlight_test_create'),
    path('highlights/test/update/', views.highlight_test_update_form, name='highlight_test_update'),
    path('highlights/<uuid:match_id>/', views.highlight_detail, name='highlight_detail'),
    path('match/<uuid:match_id>/highlights/', views.highlight_detail, name='match_highlights'),
    
    # Create operation
    path('match/<uuid:match_id>/highlights/create', views.highlight_create, name='highlight_create'),
    
    # Update operation
    path('match/<uuid:match_id>/highlights/update/', views.highlight_update, name='highlight_update'),
    
    # Delete operation
    path('match/<uuid:match_id>/highlights/delete/', views.highlight_delete, name='highlight_delete'),
]
