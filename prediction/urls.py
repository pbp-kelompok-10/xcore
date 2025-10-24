from django.urls import path
from .views import prediction_list, submit_vote, my_votes, update_vote, delete_vote

app_name = 'prediction'

urlpatterns = [
    path('', prediction_list, name='list'), # READ
    path('submit-vote/', submit_vote, name='submit_vote'), # CREATE
    path('my-votes/update/<uuid:vote_id>/', update_vote, name='update_vote'),  # UPDATE
    path('my-votes/delete/<uuid:vote_id>/', delete_vote, name='delete_vote'),  # DELETE
]
