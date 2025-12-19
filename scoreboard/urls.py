from django.urls import path, include
from scoreboard.views import (
    scoreboard_list, add_match, update_score, delete_match, 
    scoreboard_json, add_match_json, 
    add_match_flutter, edit_match_flutter, delete_match_flutter
) 
from prediction.views import prediction_list
from statistik.views import statistik_display


app_name = 'scoreboard'

urlpatterns = [
    path('', scoreboard_list, name='scoreboard_list'),
    path('add_match/', add_match, name='add_match'),
    path('update/<uuid:match_id>/', update_score, name='update_score'),
    path('prediction/', include('prediction.urls')),
    path('statistik/<uuid:match_id>/', statistik_display, name='statistik_display'),
    path('delete/<uuid:match_id>/', delete_match, name='delete_match'),
    path('json/', scoreboard_json, name='scoreboard_json'),
    path('add-json/', add_match_json, name='add_match_json'),
    path('add_match_flutter/', add_match_flutter, name='add_match_flutter'),
    path('edit_match_flutter/<uuid:match_id>/', edit_match_flutter, name='edit_match_flutter'),
    path('delete-flutter/<uuid:match_id>/', delete_match_flutter, name='delete_match_flutter'),
]
