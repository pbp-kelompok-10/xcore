from forum.views import show_main, add_post, delete_post, get_posts
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('<str:id>/', show_main, name='forum_detail'),
    path('<str:forum_id>/add_post/', add_post, name='add_post'),
    path('delete_post/<str:post_id>/', delete_post, name='delete_post'),
    path('<str:forum_id>/get_posts/', get_posts, name='get_posts'),
]