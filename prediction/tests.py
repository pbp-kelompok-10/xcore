import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from scoreboard.models import Match
from prediction.models import Prediction, Vote

User = get_user_model()


class PredictionBaseSetup(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.user = User.objects.create_user(
            username="user1",
            password="pass123",
            is_admin=False,
        )
        self.other_user = User.objects.create_user(
            username="user2",
            password="pass456",
            is_admin=False,
        )

        # Match for predictions; in the future so voting is still open initially
        self.match = Match.objects.create(
            id=uuid.uuid4(),
            home_team_code="jp",
            away_team_code="kr",
            home_score=0,
            away_score=0,
            match_date=timezone.now() + timezone.timedelta(hours=4),
            stadium="National Stadium",
            status="upcoming",
        )

        # Prediction linked to the match
        self.prediction = Prediction.objects.create(
            match=self.match,
            votes_home_team=5,
            votes_away_team=3,
        )

        # URL names must match your prediction/urls.py
        # I'm assuming:
        # path('', prediction_list, name='list')
        # path('vote/', submit_vote, name='submit_vote')
        # path('my-votes/', my_votes, name='my_votes')
        # path('vote/<uuid:vote_id>/edit/', update_vote, name='update_vote')
        # path('vote/<uuid:vote_id>/delete/', delete_vote, name='delete_vote')
        self.prediction_list_url = reverse("prediction:list")
        self.submit_vote_url = reverse("prediction:submit_vote")
        self.my_votes_url = reverse("prediction:my_votes")


class PredictionListViewTests(PredictionBaseSetup):
    def test_prediction_list_groups_by_status(self):
        """
        prediction_list should render template and split predictions
        into upcoming / live / finished based on match.status
        """
        match_live = Match.objects.create(
            id=uuid.uuid4(),
            home_team_code="jp",
            away_team_code="kr",
            home_score=1,
            away_score=0,
            match_date=timezone.now(),
            stadium="Live Arena",
            status="live",
        )
        match_finished = Match.objects.create(
            id=uuid.uuid4(),
            home_team_code="jp",
            away_team_code="kr",
            home_score=2,
            away_score=2,
            match_date=timezone.now() - timezone.timedelta(hours=4),
            stadium="Old Arena",
            status="finished",
        )

        Prediction.objects.create(match=match_live, votes_home_team=10, votes_away_team=4)
        Prediction.objects.create(match=match_finished, votes_home_team=7, votes_away_team=9)

        res = self.client.get(self.prediction_list_url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "prediction_center.html")
        self.assertIn("upcoming_predictions", res.context)
        self.assertIn("live_predictions", res.context)
        self.assertIn("finished_predictions", res.context)

        self.assertTrue(any(p.match.status == "upcoming" for p in res.context["upcoming_predictions"]))
        self.assertTrue(any(p.match.status == "live" for p in res.context["live_predictions"]))
        self.assertTrue(any(p.match.status == "finished" for p in res.context["finished_predictions"]))


class SubmitVoteTests(PredictionBaseSetup):
    def test_submit_vote_requires_login(self):
        """
        Unauthenticated user should be redirected by login_required(login_url='/login')
        """
        res = self.client.post(self.submit_vote_url, {})
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.url)

    def test_submit_vote_invalid_method(self):
        """
        GET should return {"status": "error", "message": "Invalid request"}
        """
        self.client.login(username="user1", password="pass123")
        res = self.client.get(self.submit_vote_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "error")
        self.assertEqual(res.json()["message"], "Invalid request")

    def test_submit_vote_prediction_not_found(self):
        """
        If prediction_id doesn't exist, should return error JSON.
        We pass a valid UUID that's not in DB.
        """
        self.client.login(username="user1", password="pass123")
        fake_id = uuid.uuid4()
        res = self.client.post(self.submit_vote_url, {
            "prediction_id": str(fake_id),
            "choice": "home",
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "error")
        self.assertIn("not found", res.json()["message"].lower())

    def test_submit_vote_closed_deadline(self):
        """
        If voting is closed (deadline passed), should block.
        We'll simulate closed by moving match_date to the past so is_voting_open() returns False.
        """
        self.client.login(username="user1", password="pass123")

        # force match to be in the past so deadline is passed
        self.prediction.match.match_date = timezone.now() - timezone.timedelta(hours=1)
        self.prediction.match.save()

        res = self.client.post(self.submit_vote_url, {
            "prediction_id": str(self.prediction.id),
            "choice": "home",
        })

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("ditutup", data["message"].lower())

    def test_submit_vote_duplicate_vote_blocked(self):
        """
        If user already voted on this prediction, block creating new vote
        """
        self.client.login(username="user1", password="pass123")

        # user has already voted home
        Vote.objects.create(
            user=self.user,
            prediction=self.prediction,
            choice="home"
        )

        res = self.client.post(self.submit_vote_url, {
            "prediction_id": str(self.prediction.id),
            "choice": "home",
        })

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "error")
        self.assertIn("sudah vote", res.json()["message"].lower())

    def test_submit_vote_success_updates_counts(self):
        """
        New vote should:
        - create Vote
        - increment the right counter on Prediction
        - return success json with team names + percentages
        """
        self.client.login(username="user1", password="pass123")

        # keep match date in the future so voting is open

        res = self.client.post(self.submit_vote_url, {
            "prediction_id": str(self.prediction.id),
            "choice": "home",  # should increment votes_home_team
        })

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

        # Should include home/away info
        self.assertEqual(data["home"]["team"], self.prediction.match.home_team)
        self.assertEqual(data["away"]["team"], self.prediction.match.away_team)

        # Verify it incremented
        self.prediction.refresh_from_db()
        self.assertEqual(self.prediction.votes_home_team, 6)  # 5 + 1
        self.assertEqual(self.prediction.votes_away_team, 3)

        # ensure Vote created for that user
        self.assertTrue(
            Vote.objects.filter(user=self.user, prediction=self.prediction).exists()
        )


class MyVotesViewTests(PredictionBaseSetup):
    def test_my_votes_redirect_if_not_logged_in(self):
        """
        @login_required without custom login_url uses settings.LOGIN_URL.
        We can't assume /accounts/login exactly, but we can assert 302.
        """
        res = self.client.get(self.my_votes_url)
        self.assertEqual(res.status_code, 302)
        # optional: assert it's a login-ish redirect
        self.assertIn("login", res.url.lower())

    def test_my_votes_lists_user_votes(self):
        """
        Only the logged-in user's votes should appear.
        """
        self.client.login(username="user1", password="pass123")

        my_vote = Vote.objects.create(
            user=self.user,
            prediction=self.prediction,
            choice="home",
        )
        Vote.objects.create(
            user=self.other_user,
            prediction=self.prediction,
            choice="away",
        )

        res = self.client.get(self.my_votes_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "my_votes.html")
        self.assertIn("votes", res.context)

        votes_qs = res.context["votes"]
        # first should be my_vote because of order_by('-voted_at')
        self.assertEqual(list(votes_qs)[0].id, my_vote.id)
        self.assertTrue(all(v.user == self.user for v in votes_qs))


class UpdateVoteViewTests(PredictionBaseSetup):
    def setUp(self):
        super().setUp()
        # User's existing vote
        self.vote = Vote.objects.create(
            user=self.user,
            prediction=self.prediction,
            choice="home"
        )
        self.update_url = reverse("prediction:update_vote", args=[self.vote.id])

    def test_update_vote_requires_login(self):
        res = self.client.get(self.update_url)
        self.assertEqual(res.status_code, 302)
        self.assertIn("login", res.url.lower())

    def test_update_vote_blocks_if_not_owner(self):
        """
        Non-owner should get 404 from get_object_or_404(...)
        """
        self.client.login(username="user2", password="pass456")
        res = self.client.get(self.update_url)
        self.assertEqual(res.status_code, 404)

    def test_update_vote_blocked_if_deadline_passed(self):
        """
        When voting is closed, view should:
        - add error message
        - redirect to my_votes
        """
        self.client.login(username="user1", password="pass123")

        # Close the window: put match in the past
        self.prediction.match.match_date = timezone.now() - timezone.timedelta(hours=1)
        self.prediction.match.save()

        res = self.client.get(self.update_url, follow=True)
        self.assertEqual(res.status_code, 200)

        messages = [m.message for m in get_messages(res.wsgi_request)]
        # Expect "Voting sudah ditutup! Tidak bisa ubah vote lagi."
        self.assertTrue(any("voting sudah ditutup" in m.lower() for m in messages))

    def test_update_vote_post_success_changes_choice_and_counts(self):
        """
        Switch from 'home' -> 'away'
        Should decrement home and increment away
        """
        self.client.login(username="user1", password="pass123")

        # Keep match in future so we can still modify
        res = self.client.post(self.update_url, {
            "choice": "away"
        }, follow=True)

        self.assertEqual(res.status_code, 200)

        # Reload objects and verify
        self.prediction.refresh_from_db()
        self.vote.refresh_from_db()

        self.assertEqual(self.prediction.votes_home_team, 4)  # 5 - 1
        self.assertEqual(self.prediction.votes_away_team, 4)  # 3 + 1
        self.assertEqual(self.vote.choice, "away")

        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("berhasil diubah" in m.lower() for m in msgs))


class DeleteVoteViewTests(PredictionBaseSetup):
    def setUp(self):
        super().setUp()
        self.vote = Vote.objects.create(
            user=self.user,
            prediction=self.prediction,
            choice="home"
        )
        self.delete_url = reverse("prediction:delete_vote", args=[self.vote.id])

    def test_delete_vote_requires_login(self):
        res = self.client.get(self.delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertIn("login", res.url.lower())

    def test_delete_vote_blocked_if_not_owner(self):
        self.client.login(username="user2", password="pass456")
        res = self.client.get(self.delete_url)
        self.assertEqual(res.status_code, 404)

    def test_delete_vote_blocked_if_deadline_passed_normal_request(self):
        """
        If vote.can_modify() == False (deadline passed),
        POST should:
        - add error message
        - redirect to my_votes
        """
        self.client.login(username="user1", password="pass123")

        # Force deadline passed
        self.prediction.match.match_date = timezone.now() - timezone.timedelta(hours=1)
        self.prediction.match.save()

        res = self.client.post(self.delete_url, follow=True)
        self.assertEqual(res.status_code, 200)

        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("voting sudah ditutup" in m.lower() for m in msgs))

    def test_delete_vote_blocked_if_deadline_passed_ajax(self):
        """
        If can't modify AND request is AJAX:
        Should return JSON error, not success
        """
        self.client.login(username="user1", password="pass123")

        # Force deadline passed
        self.prediction.match.match_date = timezone.now() - timezone.timedelta(hours=1)
        self.prediction.match.save()

        res = self.client.post(
            self.delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("voting sudah ditutup", data["message"].lower())

    def test_delete_vote_success_normal_request(self):
        """
        When allowed:
        - should decrement vote counts
        - delete the vote
        - flash success
        - redirect
        """
        self.client.login(username="user1", password="pass123")

        # Keep match in future => can_modify() True
        res = self.client.post(self.delete_url, follow=True)
        self.assertEqual(res.status_code, 200)

        # After deleting this user's 'home' vote, home count should decrement
        self.prediction.refresh_from_db()
        self.assertEqual(self.prediction.votes_home_team, 4)  # was 5 -> now 4
        self.assertEqual(self.prediction.votes_away_team, 3)

        # Vote should be gone
        self.assertFalse(Vote.objects.filter(id=self.vote.id).exists())

        msgs = [m.message for m in get_messages(res.wsgi_request)]
        self.assertTrue(any("berhasil dihapus" in m.lower() for m in msgs))

    def test_delete_vote_success_ajax(self):
        """
        With AJAX request and allowed modification:
        - should return JSON success
        - and delete vote
        """
        self.client.login(username="user1", password="pass123")

        res = self.client.post(
            self.delete_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("berhasil dihapus", data["message"].lower())

        self.assertFalse(Vote.objects.filter(id=self.vote.id).exists())

    def test_delete_vote_get_renders_confirmation_template(self):
        """
        GET should render confirmation page with the vote in context.
        Assumes delete_vote view returns render(...) for GET
        and that templates/delete_vote.html exists.
        """
        self.client.login(username="user1", password="pass123")

        res = self.client.get(self.delete_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "delete_vote.html")
        self.assertIn("vote", res.context)
