import io, json, zipfile, uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from lineup.models import Team, Player, Lineup
from scoreboard.models import Match

User = get_user_model()

class BaseSetup(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="admin123", is_admin=True)
        self.user = User.objects.create_user(username="user", password="user123", is_admin=False)

        self.team_home = Team.objects.create(code="jp")
        self.team_away = Team.objects.create(code="kr")

        self.match = Match.objects.create(
            home_team_code="jp",
            away_team_code="kr",
            match_date=timezone.now(),
            stadium="Tokyo Dome",
            status="finished"
        )

        for i in range(1, 12):
            Player.objects.create(nama=f"HomePlayer{i}", asal="Japan", umur=25, nomor=i, tim=self.team_home)
            Player.objects.create(nama=f"AwayPlayer{i}", asal="Korea", umur=25, nomor=i, tim=self.team_away)


class PermissionEdgeCasesTest(BaseSetup):
    def test_redirect_unauthenticated_user(self):
        """Unauthenticated user redirected to login"""
        response = self.client.get(reverse("lineup:team-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("landingpage:login"), response.url)

    def test_permission_denied_for_non_admin(self):
        """Authenticated non-admin gets 302"""
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse("lineup:team-update", args=[self.team_home.id]))
        self.assertEqual(response.status_code, 302)


class TeamUpdateViewTest(BaseSetup):
    def test_team_update_get_context_contains_formset(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("lineup:team-update", args=[self.team_home.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("player_formset", response.context)

    def test_team_update_invalid_formset(self):
        self.client.login(username="admin", password="admin123")
        url = reverse("lineup:team-update", args=[self.team_home.id])
        data = {"code": "jp"}
        response = self.client.post(url, data, follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Please correct errors" in m for m in messages))



class PlayerListViewTest(BaseSetup):
    def test_grouped_players_in_context(self):
        self.client.login(username="admin", password="admin123")
        res = self.client.get(reverse("lineup:player-list"))
        self.assertEqual(res.status_code, 200)
        grouped = res.context["grouped_teams"]
        self.assertIn(self.team_home, grouped)
        self.assertTrue(all(hasattr(p, "nama") for p in grouped[self.team_home]))


class LineupViewsTest(BaseSetup):
    def test_lineup_detail_view(self):
        self.client.login(username="admin", password="admin123")
        url = reverse("lineup:lineup-detail", args=[self.match.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "lineups/lineup_detail.html")

    def test_lineup_create_invalid_player_count(self):
        self.client.login(username="admin", password="admin123")
        url = reverse("lineup:lineup-create", args=[self.match.id])
        res = self.client.post(url, {"home_players": "1,2,3", "away_players": "1,2,3"}, follow=True)
        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("must have 11 players" in m for m in msgs))

    def test_lineup_create_success(self):
        self.client.login(username="admin", password="admin123")
        url = reverse("lineup:lineup-create", args=[self.match.id])
        home_ids = ",".join(str(p.id) for p in Player.objects.filter(tim=self.team_home)[:11])
        away_ids = ",".join(str(p.id) for p in Player.objects.filter(tim=self.team_away)[:11])
        res = self.client.post(url, {"home_players": home_ids, "away_players": away_ids})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Lineup.objects.filter(match=self.match, team=self.team_home).exists())

    def test_lineup_update_view_get_and_post(self):
        self.client.login(username="admin", password="admin123")
        Lineup.objects.create(match=self.match, team=self.team_home)
        Lineup.objects.create(match=self.match, team=self.team_away)
        url = reverse("lineup:lineup-update", args=[self.match.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res2 = self.client.post(url, {"home_players": "1,2,3,4,5,6,7,8,9,10,11", "away_players": "1,2,3,4,5,6,7,8,9,10,11"})
        self.assertEqual(res2.status_code, 302)

    def test_lineup_delete_post(self):
        self.client.login(username="admin", password="admin123")
        Lineup.objects.create(match=self.match, team=self.team_home)
        delete_url = reverse("lineup:lineup-delete", args=[self.match.id])
        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Lineup.objects.filter(match=self.match).exists())


class UploadTeamsViewTest(BaseSetup):
    def make_zip(self, files):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, json.dumps(content))
        buffer.seek(0)
        return SimpleUploadedFile("teams.zip", buffer.read(), content_type="application/zip")

    def test_upload_teams_success(self):
        self.client.login(username="admin", password="admin123")
        payload = {"team1.json": {"negara": "Japan"}, "team2.json": {"negara": "South Korea"}}
        zip_file = self.make_zip(payload)
        res = self.client.post(reverse("lineup:upload-teams"), {"file": zip_file})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_upload_teams_invalid_zip(self):
        self.client.login(username="admin", password="admin123")
        bad = SimpleUploadedFile("bad.zip", b"notazip", content_type="application/zip")
        res = self.client.post(reverse("lineup:upload-teams"), {"file": bad})
        self.assertEqual(res.status_code, 400)


class UploadPlayersViewTest(BaseSetup):
    def make_zip(self, files):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, json.dumps(content))
        buffer.seek(0)
        return SimpleUploadedFile("players.zip", buffer.read(), content_type="application/zip")

    def test_upload_players_success(self):
        self.client.login(username="admin", password="admin123")
        payload = {"team1.json": {"players": [{"nama": "New Player", "tim": self.team_home.name, "nomor": 99}]}}
        zip_file = self.make_zip(payload)
        res = self.client.post(reverse("lineup:upload-players"), {"file": zip_file})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_upload_players_invalid_zip(self):
        self.client.login(username="admin", password="admin123")
        bad = SimpleUploadedFile("bad.zip", b"brokenzip", content_type="application/zip")
        res = self.client.post(reverse("lineup:upload-players"), {"file": bad})
        self.assertEqual(res.status_code, 400)


class HelperFunctionsTest(BaseSetup):
    def test_get_teams_for_match(self):
        res = self.client.get(reverse("lineup:ajax-get-teams"), {"match": self.match.id})
        self.assertEqual(res.status_code, 200)
        self.assertIn("teams", res.json())

    def test_get_players_for_team(self):
        res = self.client.get(reverse("lineup:ajax-get-players"), {"team": self.team_home.id})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("players", data)
        self.assertTrue(any("#" in p["name"] for p in data["players"]))


class UploadEdgeCaseTest(BaseSetup):
    def test_no_file_upload(self):
        self.client.login(username="admin", password="admin123")
        res1 = self.client.post(reverse("lineup:upload-teams"))
        self.assertEqual(res1.status_code, 400)
        res2 = self.client.post(reverse("lineup:upload-players"))
        self.assertEqual(res2.status_code, 400)

    def test_non_admin_upload_forbidden(self):
        self.client.login(username="user", password="user123")
        res = self.client.post(reverse("lineup:upload-teams"))
        self.assertEqual(res.status_code, 302)


class LineupModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(code='id')
        self.player = Player.objects.create(
            nama="Bambang",
            asal="Jakarta",
            umur=28,
            nomor=9,
            tim=self.team
        )
        self.match = Match.objects.create(
            id=uuid.uuid4(),
            home_team_code='id',
            away_team_code='jp',
            home_team='Indonesia',
            away_team='Japan',
            home_score=1,
            away_score=2,
            match_date=timezone.now(),
            stadium='Gelora Bung Karno',
        )

    def test_team_save_sets_name_correctly(self):
        team = Team.objects.create(code='jp')
        self.assertEqual(team.name, 'Japan')

    def test_player_str_returns_correct_format(self):
        expected = f"{self.player.nama} ({self.team.name})"
        self.assertEqual(str(self.player), expected)

    def test_lineup_str_returns_correct_format(self):
        lineup = Lineup.objects.create(match=self.match, team=self.team)
        expected = f"Lineup for {self.team.name} in {self.match}"
        self.assertEqual(str(lineup), expected)
