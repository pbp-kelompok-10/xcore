from django.contrib import admin
from django.urls import path, include  # ⬅️ tambahkan include di sini

urlpatterns = [
    path('admin/', admin.site.urls),
    path('statistik/', include('statistik.urls')),  # ⬅️ arahkan ke app statistik
]
