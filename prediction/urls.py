from django.urls import path
from prediction.views import prediction_list, submit_vote

app_name = 'main'

urlpatterns = [
    path('', prediction_list, name='prediction_list'),
    path("submit-vote/", submit_vote, name="submit_vote")
]

