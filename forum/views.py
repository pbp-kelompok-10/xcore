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
from django.utils import timezone
from django.contrib.auth import get_user_model

def show_main(request, id):
    try:
        match = Match.objects.get(id=id)
        forum = Forum.objects.get(match=match)
        return render(request, 'main_forum.html', {'forum': forum, 'match': match})
    except (Match.DoesNotExist, Forum.DoesNotExist):
        return HttpResponse(b"Forum or Match not found.", status=404)
    
def create_forum_for_match(match):
    new_forum = Forum(
        match=match,
        nama="About " + match.home_team + " vs " + match.away_team,
    )
    new_forum.save()
    return HttpResponse(b'Forum created successfully.', status=201)

def delete_forum(request, forum_id):
    try:
        forum = Forum.objects.get(id=forum_id)
        forum.delete()
        return HttpResponse(b'Forum deleted successfully.', status=200)
    except Forum.DoesNotExist:
        pass

def edit_forum(request, forum_id):
    try:
        forum = Forum.objects.get(id=forum_id)
    except Forum.DoesNotExist:
        return HttpResponse(b'Forum not found.', status=404)

    if request.method == 'POST':
        new_name = request.POST.get('nama')
        if new_name:
            forum.nama = new_name
            forum.save()
            return HttpResponseRedirect(reverse('forum:show_main', args=[forum_id]))
        else:
            return HttpResponseBadRequest(b'Nama cannot be empty.')

    return render(request, 'edit_forum.html', {'forum': forum})

@require_POST
def add_post(request, forum_id):
    forum = Forum.objects.get(id=forum_id)
    message = request.POST.get('message')
    author = request.user
    
    if (author.is_anonymous):
        return JsonResponse({'error': 'You must be logged in to add a post.'}, status=403)
    
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

        User = get_user_model()

        posts_data = [
            {
                'id': post.id,
                'author_id': post.author.id,
                'author_name': post.author.username,
                'message': post.message,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_edited': post.is_edited,
                'edited_at': post.edited_at.strftime('%Y-%m-%d %H:%M:%S') if post.edited_at else None,
            }
            for post in posts
        ]

        return JsonResponse({
            'posts': posts_data,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'user_is_authenticated': request.user.is_authenticated,
        }, status=200)

    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)

@require_POST
def delete_post(request, forum_id, post_id):  
    try:
        post = Post.objects.get(id=post_id, forum_id=forum_id, author=request.user)
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully!'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found or unauthorized.'}, status=404)
    
    
@require_POST
def edit_post(request, forum_id, post_id):
    try:
        post = Post.objects.get(id=post_id, forum_id=forum_id, author=request.user)
        new_message = request.POST.get('message')
        new_date = timezone.now()
        
        if not new_message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
        
        post.message = new_message
        post.edited_at = new_date
        post.is_edited = True
        post.save()
        
        return JsonResponse({'message': 'Post updated successfully!'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found or unauthorized.'}, status=404)
