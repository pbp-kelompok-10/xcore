from forum.views import show_main, add_post, delete_post, get_posts, edit_post, get_forum_json, get_posts_flutter, add_post_flutter, edit_post_flutter, delete_post_flutter
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('<str:id>/', show_main, name='forum_detail'),
    path('<str:forum_id>/add_post/', add_post, name='add_post'),
    path('<str:forum_id>/delete_post/<str:post_id>/', delete_post, name='delete_post'),
    path('<str:forum_id>/edit_post/<str:post_id>/', edit_post, name='edit_post'),
    
    path('<str:forum_id>/get_posts/', get_posts, name='get_posts'),
    path('<str:match_id>/json/', get_forum_json, name='get_forum_json'),
    
    path('flutter/<str:forum_id>/get_posts/', get_posts_flutter, name='get_posts_flutter'),
    path('flutter/<str:forum_id>/add_post/', add_post_flutter, name='add_post_flutter'),
    path('flutter/<str:forum_id>/edit_post/<str:post_id>/', edit_post_flutter, name='edit_post_flutter'),
    path('flutter/<str:forum_id>/delete_post/<str:post_id>/', delete_post_flutter, name='delete_post_flutter'),
]