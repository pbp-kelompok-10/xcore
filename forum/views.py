from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Forum, Post
from scoreboard.models import Match
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from user.models import CustomUser
from django.db import models as db_models  
import json

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
        posts = Post.objects.filter(forum=forum)
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            posts = posts.filter(
                db_models.Q(message__icontains=search_query) | 
                db_models.Q(author__username__icontains=search_query)
            )
        
        # Filter by author (my posts or all posts)
        author_filter = request.GET.get('author_filter', 'all')
        if author_filter == 'my_posts' and request.user.is_authenticated:
            posts = posts.filter(author=request.user)
        
        # Sort functionality
        sort_by = request.GET.get('sort', 'newest')
        if sort_by == 'oldest':
            posts = posts.order_by('created_at')
        elif sort_by == 'edited':
            posts = posts.filter(is_edited=True).order_by('-edited_at')
        else:  # newest (default)
            posts = posts.order_by('-created_at')

        posts_data = [
            {
                'id': post.id,
                'author_id': post.author.id,
                'author_name': post.author.username,
                'message': post.message,
                'author_picture': post.author.profile_picture.url if post.author.profile_picture else None,
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
            'user_is_admin': request.user.is_admin if request.user.is_authenticated else False,
        }, status=200)

    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)

@require_POST
def delete_post(request, forum_id, post_id):  
    try:
        # Dapatkan post tanpa filter author dulu
        post = Post.objects.get(id=post_id, forum_id=forum_id)
        
        # Cek apakah user adalah author ATAU admin
        is_admin = request.user.is_admin if request.user.is_authenticated else False
        if request.user != post.author and not is_admin:
            return JsonResponse({'error': 'Not authorized to delete this post.'}, status=403)
        
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully!'}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)
    
    
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
        
        return JsonResponse({'message': 'Post updated successfully!'}, status = 200)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found or unauthorized.'}, status=404)
    

# Get forum by match ID
@csrf_exempt
@require_http_methods(["GET"])
def get_forum_json(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
        forum = Forum.objects.get(match=match)
        forum_data = {
            'id': str(forum.id),
            'nama': forum.nama,
            'match_id': match_id,
            'match_home': match.home_team,
            'match_away': match.away_team,
        }
        return JsonResponse(forum_data, status=200)
    except (Match.DoesNotExist, Forum.DoesNotExist):
        return JsonResponse({'error': 'Forum or Match not found.'}, status=404)

# Get all posts for a forum
@csrf_exempt
@require_http_methods(["GET"])
def get_posts_flutter(request, forum_id):
    try:
        forum = Forum.objects.get(id=forum_id)
        posts = Post.objects.filter(forum=forum)
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            posts = posts.filter(
                db_models.Q(message__icontains=search_query) | 
                db_models.Q(author__username__icontains=search_query)
            )
        
        # Filter by author (my posts or all posts)
        author_filter = request.GET.get('author_filter', 'all')
        if author_filter == 'my_posts' and request.user.is_authenticated:
            posts = posts.filter(author=request.user)
        
        # Sort functionality
        sort_by = request.GET.get('sort', 'newest')
        if sort_by == 'oldest':
            posts = posts.order_by('created_at')
        elif sort_by == 'edited':
            posts = posts.filter(is_edited=True).order_by('-edited_at')
        else:  # newest (default)
            posts = posts.order_by('-created_at')
        
        posts_data = []
        for post in posts:
            post_data = {
                'id': str(post.id),
                'author_id': post.author.id,
                'author_name': post.author.username,
                'author_picture': post.author.profile_picture.url if post.author.profile_picture else None,
                'message': post.message,
                'created_at': post.created_at.isoformat(), 
                'is_edited': post.is_edited,
                'edited_at': post.edited_at.isoformat() if post.edited_at else None,
            }
            posts_data.append(post_data)
        
        # debugging line
        print(f"DEBUG: User is_authenticated = {request.user.is_authenticated}, User is_admin = {request.user.is_admin if request.user.is_authenticated else 'N/A'}")
        
        return JsonResponse({
            'posts': posts_data,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'user_is_authenticated': request.user.is_authenticated,
            'user_is_admin': request.user.is_admin if request.user.is_authenticated else False,
        }, status=200)
    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def add_post_flutter(request, forum_id):
    try:
        # Cek autentikasi user
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated. Please login first.'}, status=401)
        
        # Ambil data dari POST (form data) 
        message = request.POST.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
        
        forum = Forum.objects.get(id=forum_id)
        
        # Gunakan user yang sedang login
        author = request.user
        
        post = Post.objects.create(
            forum=forum,
            author=author,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'post_id': str(post.id),
            'message': 'Post created successfully.'
        }, status=201)
        
    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Edit post
@csrf_exempt
@require_http_methods(["POST"])
def edit_post_flutter(request, forum_id, post_id):
    try:
        # Ambil data dari POST (form data) 
        new_message = request.POST.get('message', '').strip()
        
        if not new_message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
        
        forum = Forum.objects.get(id=forum_id)
        post = Post.objects.get(id=post_id, forum=forum)
        new_date = timezone.now()
        
        if request.user != post.author:
            return JsonResponse({'error': 'Not authorized to edit this post.'}, status=403)
        
        post.message = new_message
        post.edited_at = new_date
        post.is_edited = True
        post.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Post updated successfully.'
        }, status=200)
        
    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

# Delete post
@csrf_exempt
@require_http_methods(["POST"])
def delete_post_flutter(request, forum_id, post_id):
    try:
        forum = Forum.objects.get(id=forum_id)
        post = Post.objects.get(id=post_id, forum=forum)
        
        # Check if user is the author or admin
        is_admin = request.user.is_admin if request.user.is_authenticated else False
        if request.user != post.author and not is_admin:
            return JsonResponse({'error': 'Not authorized to delete this post.'}, status=403)
        
        post.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Post deleted successfully.'
        }, status=200)
        
    except Forum.DoesNotExist:
        return JsonResponse({'error': 'Forum not found.'}, status=404)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)