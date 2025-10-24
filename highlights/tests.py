from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from scoreboard.models import Match
from highlights.models import Highlight
from django.utils import timezone

User = get_user_model()

class HighlightViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin_user = User.objects.create_user(
            username="admin", password="admin123", is_admin=True
        )
        self.normal_user = User.objects.create_user(
            username="user", password="user123", is_admin=False
        )

        self.match = Match.objects.create(
            home_team_code="jp",
            away_team_code="kr",
            home_score=2,
            away_score=1,
            match_date=timezone.now(),
            stadium="Tokyo Dome",
            status="finished"
        )

        self.detail_url = reverse("highlights:match_highlights", args=[self.match.id])
        self.create_url = reverse("highlights:highlight_create", args=[self.match.id])
        self.update_url = reverse("highlights:highlight_update", args=[self.match.id])
        self.delete_url = reverse("highlights:highlight_delete", args=[self.match.id])

    def test_highlight_detail_view(self):
        """Should render highlight detail page correctly."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "highlight.html")
        self.assertIn("match", response.context)

    def test_highlight_create_forbidden_for_non_admin(self):
        """Non-admin users should not be able to create highlights."""
        self.client.login(username="user", password="user123")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)

    def test_highlight_create_as_admin(self):
        """Admin should be able to create highlight."""
        self.client.login(username="admin", password="admin123")
        data = {
            "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Highlight.objects.filter(match=self.match).exists())

    def test_highlight_update_as_admin(self):
        """Admin can update existing highlight."""
        highlight = Highlight.objects.create(
            match=self.match,
            video="https://www.youtube.com/watch?v=oldvideo"
        )
        self.client.login(username="admin", password="admin123")
        response = self.client.post(self.update_url, {
            "video": "https://www.youtube.com/watch?v=newvideo",
        })
        self.assertEqual(response.status_code, 302)
        highlight.refresh_from_db()
        self.assertEqual(highlight.video, "https://www.youtube.com/watch?v=newvideo")

    def test_highlight_update_forbidden_for_non_admin(self):
        """Non-admin cannot update highlight."""
        Highlight.objects.create(
            match=self.match,
            video="https://www.youtube.com/watch?v=test"
        )
        self.client.login(username="user", password="user123")
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 302)

    def test_highlight_delete_as_admin(self):
        """Admin can delete highlight."""
        Highlight.objects.create(
            match=self.match,
            video="https://www.youtube.com/watch?v=deleteme"
        )
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Highlight.objects.filter(match=self.match).exists())

    def test_highlight_delete_forbidden_for_non_admin(self):
        """Non-admin cannot delete highlight."""
        Highlight.objects.create(
            match=self.match,
            video="https://www.youtube.com/watch?v=test"
        )
        self.client.login(username="user", password="user123")
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
