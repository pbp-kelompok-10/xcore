from django.urls import path
from scoreboard.views import scoreboard_list, admin_check, add_match, update_score

app_name = 'scoreboard'

urlpatterns = [
    path('', scoreboard_list, name='scoreboard_list'),
    path('add_match/', add_match, name='add-match'),
    path('update/<int:match_id>/', update_score, name='update_score'),
]
