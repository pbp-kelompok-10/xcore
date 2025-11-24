from django.urls import path
from .views import prediction_list, submit_vote, my_votes, update_vote, delete_vote, show_json

app_name = 'prediction'

urlpatterns = [
    path('', prediction_list, name='list'),
    path('submit-vote/', submit_vote, name='submit_vote'),
    path('update-vote/', update_vote, name='update_vote'),  
    path('my-votes/', my_votes, name='my_votes'),
    path('my-votes/delete/<uuid:vote_id>/', delete_vote, name='delete_vote'),  
    path('json/', show_json, name='show_json'),
]