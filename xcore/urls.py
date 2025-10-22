from django.urls import path, include

urlpatterns = [
    path('statistik/', include('statistik.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    path('', include('highlights.urls')),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('statistik/', include('statistik.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    path('', include('highlights.urls')),
    path('', include('lineup.urls')),
]

