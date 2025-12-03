from django.urls import path
from . import views

app_name = 'highlights'

urlpatterns = [
    path('<uuid:match_id>/', views.highlight_detail, name='match_highlights'),
    path('<uuid:match_id>/create', views.highlight_create, name='highlight_create'),
    path('<uuid:match_id>/update/', views.highlight_update, name='highlight_update'),
    path('<uuid:match_id>/delete/', views.highlight_delete, name='highlight_delete'),
    path('api/<uuid:match_id>/', views.api_highlight_detail, name='api_highlight_detail'),
    path('api/<uuid:match_id>/create/', views.api_highlight_create, name='api_highlight_create'),
    path('api/<uuid:match_id>/update/', views.api_highlight_update, name='api_highlight_update'),
    path('api/<uuid:match_id>/delete/', views.api_highlight_delete, name='api_highlight_delete'),
]
