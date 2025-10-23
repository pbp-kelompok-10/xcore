from django.urls import path
from scoreboard.views import scoreboard_list, admin_check, add_match, update_score
from prediction.views import prediction_list
from statistik.views import statistik_display

app_name = 'scoreboard'

urlpatterns = [
    path('', scoreboard_list, name='scoreboard_list'),
    path('add_match/', add_match, name='add_match'),
    path('update/<uuid:match_id>/', update_score, name='update_score'),
    path('prediction/<uuid:match_id>/', prediction_list, name='prediction'),
    path('statistik/<uuid:match_id>/', statistik_display, name='statistik_display')
]
