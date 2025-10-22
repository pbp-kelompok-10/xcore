from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scoreboard/', include('scoreboard.urls')),
    path('prediction/', include('prediction.urls')),
    path('statistik/', include('statistik.urls')),
    path('lineup/', include('lineup.urls')),
    path('highlight/', include('highlights.urls', namespace='highlight')),
    path('', include('landingpage.urls')),
]
