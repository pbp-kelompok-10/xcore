import uuid
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from scoreboard.models import Match
from statistik.models import Statistik

User = get_user_model()


class StatistikViewTests(TestCase):
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
            stadium="National Stadium",
            status="finished",
        )

        self.add_url = reverse("statistik:add_statistik", args=[self.match.id])
        self.update_url = reverse("statistik:update_statistik", args=[self.match.id])
        self.delete_url = reverse("statistik:delete_statistik", args=[self.match.id])
        self.display_url = reverse("statistik:statistik_display", args=[self.match.id])

        self.valid_data = {
            "pass_home": 100,
            "pass_away": 90,
            "shoot_home": 8,
            "shoot_away": 6,
            "on_target_home": 4,
            "on_target_away": 3,
            "ball_possession_home": 55.0,
            "ball_possession_away": 45.0,
            "red_card_home": 0,
            "red_card_away": 1,
            "yellow_card_home": 2,
            "yellow_card_away": 3,
            "offside_home": 1,
            "offside_away": 2,
            "corner_home": 5,
            "corner_away": 4,
        }

    def test_display_view_shows_statistik(self):
        statistik = Statistik.objects.create(match=self.match, **self.valid_data)
        res = self.client.get(self.display_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "statistik/statistik_display.html")
        self.assertEqual(res.context["statistik"], statistik)
        self.assertEqual(res.context["match"], self.match)

    def test_add_requires_admin(self):
        """Non-admin should be redirected to display page."""
        self.client.login(username="user", password="pass456")
        res = self.client.get(self.add_url)
        self.assertEqual(res.status_code, 302)
        self.assertIn(str(self.match.id), res.url)

    def test_add_admin_get_form(self):
        """Admin should see statistik form page."""
        self.client.login(username="admin", password="pass123")
        res = self.client.get(self.add_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "statistik/statistik_form.html")

    def test_add_admin_post_valid_normal(self):
        """POST (normal) should create statistik and redirect."""
        self.client.login(username="admin", password="pass123")
        data = {"match": self.match.id, **self.valid_data}
        res = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Statistik.objects.filter(match=self.match).exists())
        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("berhasil ditambahkan" in m.lower() for m in msgs))

    def test_add_admin_post_valid_ajax(self):
        """POST (AJAX) should return JSON success."""
        self.client.login(username="admin", password="pass123")
        payload = json.dumps({"match": str(self.match.id), **self.valid_data})
        res = self.client.post(
            self.add_url,
            data=payload,
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("berhasil ditambahkan", data["message"])

    def test_add_duplicate_statistik_redirect_or_json(self):
        """If statistik exists -> show warning or JSON error."""
        Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="admin", password="pass123")

        res = self.client.post(self.add_url, {"match": self.match.id, **self.valid_data}, follow=True)
        self.assertEqual(res.status_code, 200)
        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("sudah ada" in m.lower() for m in msgs))

        res = self.client.post(
            self.add_url,
            data=json.dumps({"match": str(self.match.id), **self.valid_data}),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "error")

    def test_update_requires_admin(self):
        Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="user", password="pass456")
        res = self.client.post(self.update_url)
        self.assertEqual(res.status_code, 302)

    def test_update_admin_post_valid_normal(self):
        statistik = Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="admin", password="pass123")
        updated_data = {"match": self.match.id, **self.valid_data, "shoot_home": 10}
        res = self.client.post(self.update_url, updated_data, follow=True)
        statistik.refresh_from_db()
        self.assertEqual(statistik.shoot_home, 10)
        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("berhasil diupdate" in m.lower() for m in msgs))

    def test_update_admin_post_valid_ajax(self):
        statistik = Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="admin", password="pass123")
        payload = json.dumps({"match": str(self.match.id), **self.valid_data, "shoot_home": 12})
        res = self.client.post(
            self.update_url,
            data=payload,
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("berhasil diupdate", data["message"])

    def test_delete_requires_admin(self):
        Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="user", password="pass456")
        res = self.client.post(self.delete_url)
        self.assertEqual(res.status_code, 302)

    def test_delete_admin_post_valid_normal(self):
        Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="admin", password="pass123")
        res = self.client.post(self.delete_url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Statistik.objects.filter(match=self.match).exists())
        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("berhasil dihapus" in m.lower() for m in msgs))

    def test_delete_admin_post_valid_ajax(self):
        Statistik.objects.create(match=self.match, **self.valid_data)
        self.client.login(username="admin", password="pass123")
        res = self.client.post(
            self.delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("berhasil dihapus", data["message"])
