from django.urls import path
from .views import prediction_list, submit_vote, my_votes, update_vote, delete_vote, show_json, submit_vote_flutter, update_vote_flutter, delete_vote_flutter, show_my_votes_json

app_name = 'prediction'

urlpatterns = [
    path('', prediction_list, name='list'),
    path('submit-vote/', submit_vote, name='submit_vote'),
    path('update-vote/', update_vote, name='update_vote'),  
    path('my-votes/', my_votes, name='my_votes'),
    path('my-votes/delete/<uuid:vote_id>/', delete_vote, name='delete_vote'),  
    path('json/', show_json, name='show_json'),
    path('submit-vote-flutter/', submit_vote_flutter, name='submit_vote_flutter'),
    path('update-vote-flutter/', update_vote_flutter, name='update_vote_flutter'),
    path('delete-vote-flutter/', delete_vote_flutter, name='delete_vote_flutter'),
    path('json-my-votes/', show_my_votes_json, name='show_my_votes_json'),
]
