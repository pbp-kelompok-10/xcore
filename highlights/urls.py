from django.urls import path
from . import views

app_name = 'highlights'

urlpatterns = [
    path('<uuid:match_id>/', views.highlight_detail, name='match_highlights'),
    
    # Create operation
    path('<uuid:match_id>/create', views.highlight_create, name='highlight_create'),

    # Update operation
    path('<uuid:match_id>/update/', views.highlight_update, name='highlight_update'),

    # Delete operation
    path('<uuid:match_id>/delete/', views.highlight_delete, name='highlight_delete'),
]
