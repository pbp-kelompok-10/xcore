from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from user.forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class LandingPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('landingpage:register')
        self.login_url = reverse('landingpage:login')
        self.logout_url = reverse('landingpage:logout')
        self.home_url = reverse('landingpage:home')
        self.profile_url = reverse('landingpage:profile')

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_landing_home_view(self):
        """Landing page renders correctly"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertIn('features', response.context)
        self.assertIn('title', response.context)

    def test_register_get_request(self):
        """GET request to register page renders form"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_valid_data(self):
        """POST valid registration data creates a user and redirects"""
        data = {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Your account has been successfully created!", messages[0])

    def test_register_post_invalid_data(self):
        """POST invalid registration data should re-render form with errors"""
        data = {
            'username': 'invaliduser',
            'password1': 'abc',
            'password2': 'xyz',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertFalse(User.objects.filter(username='invaliduser').exists())

    def test_login_get_request(self):
        """GET request to login page renders AuthenticationForm"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_valid_credentials(self):
        """POST valid credentials logs user in and redirects to home"""
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

    def test_login_post_invalid_credentials(self):
        """POST invalid credentials keeps user on login page"""
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_logout_user_redirects_to_login(self):
        """Logging out redirects to login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.login_url)

    def test_profile_view(self):
        """Profile page renders correctly"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
