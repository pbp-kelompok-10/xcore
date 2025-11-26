from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('statistik/', include('statistik.urls')),
    path('scoreboard/', include('scoreboard.urls')),
    path('prediction/', include('prediction.urls')),
    path('lineup/', include('lineup.urls')),
    path('highlight/', include('highlights.urls', namespace='highlight')),
    path('', include('landingpage.urls')),
    path('forum/', include('forum.urls', namespace='forum')),
    path('user/', include('user.urls', namespace='user')),
    path('auth/', include('authentication.urls', namespace='authentication')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
