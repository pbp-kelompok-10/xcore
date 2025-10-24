from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path("create-admin/", views.create_admin_user, name="create-admin"),
]
