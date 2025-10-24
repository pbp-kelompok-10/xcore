from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Forum, Post
from .forms import PostForm, ForumForm
from scoreboard.models import Match
import uuid
from datetime import datetime, timedelta

class ForumTestCase(TestCase):
    def setUp(self):
        # Buat Match dengan SEMUA field wajib
        self.match = Match.objects.create(
            id=uuid.uuid4(),
            home_team="Team A",
            away_team="Team B",
            match_date=timezone.now(),  # **WAJIB: tambahkan match_date**
            # Tambahkan field lain yang wajib sesuai model Match Anda
            # Contoh: stadium="Stadium Test", competition="Test League"
        )
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(match=self.match, nama="About Team A vs Team B")
        self.post = Post.objects.create(forum=self.forum, author=self.user, message="Test post")

    def test_forum_model_str(self):
        """Test method __str__ of Forum model"""
        self.assertEqual(str(self.forum), "About Team A vs Team B")

    def test_post_model_str(self):
        """Test method __str__ of Post model"""
        expected_str = f"{self.post.id}-{self.forum.id}"
        self.assertEqual(str(self.post), expected_str)

    def test_forum_creation(self):
        """Test creation of a new Forum"""
        new_match = Match.objects.create(
            id=uuid.uuid4(),
            home_team="Team C",
            away_team="Team D",
            match_date=timezone.now()  # **WAJIB**
        )
        new_forum = Forum.objects.create(match=new_match, nama="About Team C vs Team D")
        self.assertEqual(new_forum.nama, "About Team C vs Team D")
        self.assertEqual(new_forum.match, new_match)

    def test_post_creation(self):
        """Test creation of a new Post"""
        new_post = Post.objects.create(forum=self.forum, author=self.user, message="New test post")
        self.assertEqual(new_post.message, "New test post")
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.forum, self.forum)
        self.assertTrue(new_post.created_at is not None)
        self.assertFalse(new_post.is_edited)

class ForumFormTestCase(TestCase):
    def test_forum_form_valid(self):
        """Test if ForumForm is valid with correct data"""
        form_data = {'nama': 'Test Forum'}
        form = ForumForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_forum_form_invalid_empty_nama(self):
        """Test if ForumForm is invalid with empty nama"""
        form_data = {'nama': ''}
        form = ForumForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nama', form.errors)

    def test_forum_form_strips_tags(self):
        """Test if ForumForm strips HTML tags from nama"""
        form_data = {'nama': '<script>alert("test")</script>Test Forum'}
        form = ForumForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['nama'], 'alert("test")Test Forum')

class PostFormTestCase(TestCase):
    def test_post_form_valid(self):
        """Test if PostForm is valid with correct data"""
        form_data = {'message': 'Test message'}
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_invalid_empty_message(self):
        """Test if PostForm is invalid with empty message"""
        form_data = {'message': ''}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_post_form_strips_tags(self):
        """Test if PostForm strips HTML tags from message"""
        form_data = {'message': '<script>alert("test")</script>Test message'}
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['message'], 'alert("test")Test message')

class ForumViewTestCase(TestCase):
    def setUp(self):
        # Buat Match dengan SEMUA field wajib
        self.match = Match.objects.create(
            id=uuid.uuid4(),
            home_team="Team A",
            away_team="Team B",
            match_date=timezone.now()  # **WAJIB**
        )
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.forum = Forum.objects.create(match=self.match, nama="About Team A vs Team B")
        self.post = Post.objects.create(forum=self.forum, author=self.user, message="Test post")
        self.client.login(username='testuser', password='testpass123')

    def test_show_main_success(self):
        """Test show_main view with valid match and forum"""
        response = self.client.get(reverse('forum:forum_detail', args=[self.match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_forum.html')
        self.assertIn('forum', response.context)
        self.assertIn('match', response.context)

    def test_show_main_not_found(self):
        """Test show_main view with invalid match or forum"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('forum:forum_detail', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)

    def test_add_post_success(self):
        """Test add_post view with valid data"""
        data = {
            'message': 'New post test',
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(reverse('forum:add_post', args=[self.forum.id]), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.filter(forum=self.forum, author=self.user).count(), 2)

    def test_add_post_empty_message(self):
        """Test add_post view with empty message"""
        data = {
            'message': '',
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(reverse('forum:add_post', args=[self.forum.id]), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Message cannot be empty.')

    def test_get_posts_success(self):
        """Test get_posts view with valid forum"""
        response = self.client.get(reverse('forum:get_posts', args=[self.forum.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('posts', data)
        self.assertEqual(len(data['posts']), 1)
        self.assertEqual(data['posts'][0]['message'], 'Test post')

    def test_get_posts_not_found(self):
        """Test get_posts view with invalid forum"""
        invalid_id = uuid.uuid4()
        response = self.client.get(reverse('forum:get_posts', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Forum not found.')

    def test_delete_post_success(self):
        """Test delete_post view with valid post"""
        data = {'csrfmiddlewaretoken': 'testtoken'}
        response = self.client.post(reverse('forum:delete_post', args=[self.forum.id, self.post.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 0)

    def test_delete_post_unauthorized(self):
        """Test delete_post view with unauthorized user"""
        self.client.logout()
        other_user = User.objects.create_user(username='otheruser', password='otherpass123')
        self.client.login(username='otheruser', password='otherpass123')
        data = {'csrfmiddlewaretoken': 'testtoken'}
        response = self.client.post(reverse('forum:delete_post', args=[self.forum.id, self.post.id]), data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_edit_post_success(self):
        """Test edit_post view with valid data"""
        data = {
            'message': 'Edited test post',
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(reverse('forum:edit_post', args=[self.forum.id, self.post.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        updated_post = Post.objects.get(id=self.post.id)
        self.assertEqual(updated_post.message, 'Edited test post')
        self.assertTrue(updated_post.is_edited)

    def test_edit_post_empty_message(self):
        """Test edit_post view with empty message"""
        data = {
            'message': '',
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(reverse('forum:edit_post', args=[self.forum.id, self.post.id]), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Message cannot be empty.')

    def test_edit_post_unauthorized(self):
        """Test edit_post view with unauthorized user"""
        self.client.logout()
        other_user = User.objects.create_user(username='otheruser', password='otherpass123')
        self.client.login(username='otheruser', password='otherpass123')
        data = {
            'message': 'Unauthorized edit',
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(reverse('forum:edit_post', args=[self.forum.id, self.post.id]), data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())