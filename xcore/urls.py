from django.urls import path, include

urlpatterns = [
    path('statistik/', include('statistik.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    # path('', include('prediction.urls')),
    # path('statistics/', include('statistics.urls')),
]