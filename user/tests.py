from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class CreateAdminUserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser("root", "root@example.com", "pass123")
        self.url = reverse("user:create-admin")

    def test_create_admin_user_success(self):
        self.client.login(username="root", password="pass123")
        data = {"username": "newadmin", "password": "pass456", "email": "admin@example.com"}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newadmin", is_admin=True).exists())

    def test_duplicate_username_blocked(self):
        User.objects.create_user(username="dupe", password="x")
        self.client.login(username="root", password="pass123")
        response = self.client.post(self.url, {"username": "dupe", "password": "123"}, follow=True)
        self.assertContains(response, "already exists")
