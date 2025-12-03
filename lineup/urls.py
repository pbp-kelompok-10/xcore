from django.urls import path
from .views import *

app_name = 'lineup'

urlpatterns = [
    path('upload/teams/', UploadTeamsView.as_view(), name='upload-teams'),
    path('upload/players/', UploadPlayersView.as_view(), name='upload-players'),

    path('teams/', TeamListView.as_view(), name='team-list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('teams/create/', TeamCreateView.as_view(), name='team-create'),
    path('teams/<int:pk>/update/', TeamUpdateView.as_view(), name='team-update'),

    path('players/', PlayerListView.as_view(), name='player-list'),
    path('players/<int:pk>/', PlayerDetailView.as_view(), name='player-detail'),
    path('players/create/', PlayerCreateView.as_view(), name='player-create'),
    path('players/<int:pk>/update/', PlayerUpdateView.as_view(), name='player-update'),
    path('players/<int:pk>/delete/', PlayerDeleteView.as_view(), name='player-delete'),

    path('<uuid:match_id>/', LineupDetailView.as_view(), name='lineup-detail'),
    path('create/<uuid:match_id>/', LineupCreateView.as_view(), name='lineup-create'),
    path('update/<uuid:match_id>/', LineupUpdateView.as_view(), name='lineup-update'),
    path('delete/<uuid:match_id>/', LineupDeleteView.as_view(), name='lineup-delete'),
    
    path('flutter/<uuid:match_id>/', FlutterLineupDetailView.as_view(), name='flutter-lineup-detail'),
    path('flutter/create/<uuid:match_id>/', FlutterLineupCreateView.as_view(), name='flutter-lineup-create'),
    path('flutter/update/<uuid:lineup_id>/', FlutterLineupUpdateView.as_view(), name='flutter-lineup-update'),
    path('flutter/delete/<uuid:lineup_id>/', FlutterLineupDeleteView.as_view(), name='flutter-lineup-delete'),

    path('ajax/get-teams/', get_teams_for_match, name='ajax-get-teams'),
    path('ajax/get-players/', get_players_for_team, name='ajax-get-players'),
]
