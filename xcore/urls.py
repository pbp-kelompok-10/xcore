from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('statistik/', include('statistik.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    path('prediction/', include('prediction.urls')),
    path('statistik/', include('statistik.urls')),
    path('lineup/', include('lineup.urls')),
    path('highlight/', include('highlights.urls', namespace='highlight')),
    path('', include('landingpage.urls')),
    path('forum/', include('forum.urls', namespace='forum')),
=======
    path('prediction/', include('prediction.urls')),
    path('', include('landingpage.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    # path('statistics/', include('statistics.urls')),
    path('forum/', include('forum.urls')),
>>>>>>> 1d9673b993e484d901ce888b3fa0221681fd16d5
]

