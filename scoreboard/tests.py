import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from scoreboard.models import Match
from forum.models import Forum
from prediction.models import Prediction

User = get_user_model()


class ScoreboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin_user = User.objects.create_user(
            username="admin", password="pass123", is_admin=True
        )
        self.normal_user = User.objects.create_user(
            username="user", password="pass456", is_admin=False
        )

        self.match = Match.objects.create(
            id=uuid.uuid4(),
            home_team_code="jp",
            away_team_code="kr",
            home_score=0,
            away_score=0,
            match_date=timezone.now() + timezone.timedelta(days=1),
            stadium="Tokyo Dome",
            status="upcoming",
        )

        self.scoreboard_list_url = reverse("scoreboard:scoreboard_list")
        self.add_match_url = reverse("scoreboard:add_match")
        self.update_score_url = reverse("scoreboard:update_score", args=[self.match.id])
        self.delete_match_url = reverse("scoreboard:delete_match", args=[self.match.id])

    def test_scoreboard_list_loads_and_groups_matches(self):
        res = self.client.get(self.scoreboard_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "scoreboard_list.html")
        self.assertIn("matches_by_date", res.context)
        grouped = res.context["matches_by_date"]
        self.assertTrue(any(isinstance(v, list) for v in grouped.values()))

    def test_add_match_requires_admin(self):
        """Non-admin user should get 302"""
        self.client.login(username="user", password="pass456")
        res = self.client.get(self.add_match_url)
        self.assertEqual(res.status_code, 302)

    def test_add_match_admin_gets_form(self):
        """Admin should see the form page"""
        self.client.login(username="admin", password="pass123")
        res = self.client.get(self.add_match_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "add_match.html")

    def test_update_score_requires_admin(self):
        self.client.login(username="user", password="pass456")
        res = self.client.get(self.update_score_url)
        self.assertEqual(res.status_code, 302)

    def test_update_score_admin_can_post(self):
        """Admin should update match fields"""
        self.client.login(username="admin", password="pass123")
        data = {
            "home_score": 3,
            "away_score": 1,
            "status": "finished",
            "round": 2,
            "group": "A",
            "stadium": "Osaka Arena",
        }
        res = self.client.post(self.update_score_url, data, follow=True)
        self.assertEqual(res.status_code, 200)

        self.match.refresh_from_db()
        self.assertEqual(self.match.home_score, 3)
        self.assertEqual(self.match.away_score, 1)
        self.assertEqual(self.match.status, "finished")
        self.assertEqual(self.match.stadium, "Osaka Arena")

    def test_delete_match_requires_admin(self):
        self.client.login(username="user", password="pass456")
        res = self.client.post(self.delete_match_url)
        self.assertEqual(res.status_code, 302)

    def test_delete_match_admin_post_deletes_match(self):
        """Admin should delete match successfully"""
        self.client.login(username="admin", password="pass123")
        res = self.client.post(self.delete_match_url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Match.objects.filter(id=self.match.id).exists())
