from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Forum, Post
from scoreboard.models import Match
from django.contrib.auth.models import User

def show_main(request, id):
    try:
        match = Match.objects.get(id=id)
        forum = Forum.objects.get(match=match)
        return render(request, 'main_forum.html', {'forum': forum})
    except (Match.DoesNotExist, Forum.DoesNotExist):
        return HttpResponse(b"Forum or Match not found.", status=404)

@login_required(login_url='/login/')
@require_POST
def add_post(request, forum_id):
    forum = Forum.objects.get(id=forum_id)
    message = request.POST.get('message')
    author = request.user

    if not message:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    new_post = Post(
        forum=forum,
        message=message,
        author=author
    )
    new_post.save()
    
    return HttpResponse(b'Post added successfully.', status=201)

def get_posts(request, forum_id):
    try:
        forum = Forum.objects.get(id=forum_id)
        posts = Post.objects.filter(forum=forum).order_by('created_at')
        posts_data = [
            {
                'id': post.id,
                'author_name': User.objects.get(id=post.author.id).username,
                'message': post.message,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for post in posts
        ]
        return JsonResponse({'posts': posts_data}, status=200)
    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)

# @require_POST
# def add_post(request, forum_id):
#     forum = Forum.objects.get(id=forum_id)
#     author = request.user
#     message = request.POST.get('message')

#     if not message:
#         return HttpResponseBadRequest("Message cannot be empty.")

#     new_post = Post(forum=forum, message=message, author=author)
#     new_post.save()

#     return HttpResponse(b"Post added successfully.", status=201)

def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return HttpResponseRedirect(reverse('forum:show_main', args=[post.forum.id]))
    except Post.DoesNotExist:
        return HttpResponse(b"Post not found.", status=404)
    
    
    
