from django.urls import path
from .views import *
app_name = 'lineup'
urlpatterns = [
    # ---------- Upload Endpoints ----------
    path('upload/', upload_page, name='upload-page'),
    path('upload/teams/', UploadTeamsView.as_view(), name='upload-teams'),
    path('upload/players/', UploadPlayersView.as_view(), name='upload-players'),

    # ---------- Team CRUD ----------
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('teams/create/', TeamCreateView.as_view(), name='team-create'),
    path('teams/<int:pk>/update/', TeamUpdateView.as_view(), name='team-update'),
    path('teams/<int:pk>/delete/', TeamDeleteView.as_view(), name='team-delete'),

    # ---------- Player CRUD ----------
    path('players/', PlayerListView.as_view(), name='player-list'),
    path('players/<int:pk>/', PlayerDetailView.as_view(), name='player-detail'),
    path('players/create/', PlayerCreateView.as_view(), name='player-create'),
    path('players/<int:pk>/update/', PlayerUpdateView.as_view(), name='player-update'),
    path('players/<int:pk>/delete/', PlayerDeleteView.as_view(), name='player-delete'),

    # ---------- Lineup CRUD ----------
    path('lineup/<int:match_id>/', LineupDetailView.as_view(), name='lineup-detail'),
    path('lineup/create/<int:match_id>/', LineupCreateView.as_view(), name='lineup-create'),
    path('lineup/update/<int:match_id>/', LineupUpdateView.as_view(), name='lineup-update'),
    path('lineup/delete/<int:match_id>/', LineupDeleteView.as_view(), name='lineup-delete'),

    path('ajax/get-teams/', get_teams_for_match, name='ajax-get-teams'),
    path('ajax/get-players/', get_players_for_team, name='ajax-get-players'),


]
