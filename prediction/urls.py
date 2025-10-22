from django.urls import path
from prediction.views import prediction_list

app_name = 'main'

urlpatterns = [
    path('', prediction_list, name='prediction_list'),
]

