import io
import json
import zipfile
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy,reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Team, Player, Lineup, COUNTRY_CHOICES
from .forms import LineupForm, TeamForm
from scoreboard.models import Match
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django import forms
from django.shortcuts import get_object_or_404
import base64
class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict access to admin users only with toast message."""

    def test_func(self):
        return getattr(self.request.user, "is_admin", False)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Silakan login terlebih dahulu untuk melanjutkan.")
            return redirect("landingpage:login")

        messages.error(self.request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect("/scoreboard/") 

class TeamListView(ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'


class TeamDetailView(DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'


class TeamCreateView(SuperuserRequiredMixin, CreateView):
    model = Team
    fields = ['code']
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('lineup:team-list')


class TeamUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('lineup:team-list')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Team updated successfully!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Please correct errors in the form.")
        return super().form_invalid(form)

class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/player_detail.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object

        lineup = player.lineups.first()
        context['match'] = lineup.match if lineup else None
        context['match_id_safe'] = lineup.match.id if lineup else None
        return context


class PlayerCreateView(SuperuserRequiredMixin, CreateView):
    model = Player
    fields = ['nama', 'asal', 'umur', 'nomor', 'tim']
    template_name = 'players/player_form.html'
    def get_success_url(self):
        return reverse('lineup:player-list')


class PlayerUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Player
    fields = ['nama', 'asal', 'umur', 'nomor', 'tim']
    template_name = 'players/player_form.html'

    def get_success_url(self):
        return reverse('lineup:player-detail', kwargs={'pk': self.object.pk})


class PlayerDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Player

    def get(self, request, *args, **kwargs):
        return redirect(reverse('lineup:player-list'))

    def post(self, request, *args, **kwargs):
        player = get_object_or_404(Player, pk=self.kwargs['pk'])
        player.delete()
        return redirect(reverse('lineup:player-list'))
    
class PlayerListView(TemplateView):
    template_name = 'players/player_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Team.objects.all().order_by('name')
        grouped = {}
        for team in teams:
            players = team.players.all().order_by('nomor')
            if players.exists():
                grouped[team] = players
        context['grouped_teams'] = grouped
        return context

class LineupDetailView(DetailView):
    model = Match
    template_name = 'lineups/lineup_detail.html'
    context_object_name = 'match'
    pk_url_kwarg = 'match_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.get_object()

        home_lineup = Lineup.objects.filter(match=match, team__code=match.home_team_code).first()
        away_lineup = Lineup.objects.filter(match=match, team__code=match.away_team_code).first()

        context.update({
            'home_lineup': home_lineup,
            'away_lineup': away_lineup,
        })
        return context

# API untuk Flutter - Get Lineup by Match
@method_decorator(csrf_exempt, name='dispatch')
class FlutterLineupDetailView(View):
    def get(self, request, match_id):
        try:
            match = get_object_or_404(Match, pk=match_id)
            
            home_lineup = Lineup.objects.filter(match=match, team__code=match.home_team_code).first()
            away_lineup = Lineup.objects.filter(match=match, team__code=match.away_team_code).first()
            
            # Serialize match data
            match_data = {
                'id': str(match.id),
                'home_team': match.home_team,
                'away_team': match.away_team,
                'home_team_code': match.home_team_code,
                'away_team_code': match.away_team_code,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'match_date': match.match_date.isoformat(),
                'stadium': match.stadium,
                'round': match.round,
                'group': match.group,
                'status': match.status,
            }
            
            # Serialize home lineup
            home_lineup_data = None
            if home_lineup:
                home_lineup_data = {
                    'id': str(home_lineup.id),
                    'team': {
                        'id': str(home_lineup.team.id),
                        'name': home_lineup.team.name,
                        'code': home_lineup.team.code,
                    },
                    'players': [
                        {
                            'id': str(player.id),
                            'nama': player.nama,
                            'asal': player.asal,
                            'umur': player.umur,
                            'nomor': player.nomor,
                            'tim': str(player.tim.id),
                        }
                        for player in home_lineup.players.all()
                    ]
                }
            
            # Serialize away lineup
            away_lineup_data = None
            if away_lineup:
                away_lineup_data = {
                    'id': str(away_lineup.id),
                    'team': {
                        'id': str(away_lineup.team.id),
                        'name': away_lineup.team.name,
                        'code': away_lineup.team.code,
                    },
                    'players': [
                        {
                            'id': str(player.id),
                            'nama': player.nama,
                            'asal': player.asal,
                            'umur': player.umur,
                            'nomor': player.nomor,
                            'tim': str(player.tim.id),
                        }
                        for player in away_lineup.players.all()
                    ]
                }
            
            response_data = {
                'match': match_data,
                'home_lineup': home_lineup_data,
                'away_lineup': away_lineup_data,
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class LineupCreateView(SuperuserRequiredMixin, CreateView):
    model = Lineup
    form_class = LineupForm
    template_name = 'lineups/lineup_form.html'

    def get_initial(self):
        """Automatically prefill the match field from the URL."""
        initial = super().get_initial()
        match = Match.objects.get(pk=self.kwargs['match_id'])
        initial['match'] = match
        return initial

    def get_form(self, form_class=None):
        """Hide the match field so user can’t change it."""
        form = super().get_form(form_class)
        form.fields['match'].widget = forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        """Pass match and team info to the template."""
        context = super().get_context_data(**kwargs)
        match = Match.objects.get(pk=self.kwargs['match_id'])
        context.update({
            'match': match,
            'is_edit': False,
        })
        return context

    def post(self, request, *args, **kwargs):
        """Handle lineup creation and player assignment."""
        match = Match.objects.get(pk=self.kwargs['match_id'])
        home_players_raw = request.POST.get('home_players', '')
        away_players_raw = request.POST.get('away_players', '')

        def parse_ids(raw):
            return [int(pid) for pid in raw.split(',') if pid.strip().isdigit()]

        home_ids = parse_ids(home_players_raw)
        away_ids = parse_ids(away_players_raw)

        home_team = Team.objects.filter(code=match.home_team_code).first()
        away_team = Team.objects.filter(code=match.away_team_code).first()

        if home_team:
            if len(home_ids) != 11:
                messages.error(request, f"{home_team.name} must have 11 players.")
                return redirect(request.path)

            home_lineup, _ = Lineup.objects.get_or_create(match=match, team=home_team)
            home_lineup.players.set(home_ids)
            home_lineup.save()

        if away_team:
            if len(away_ids) != 11:
                messages.error(request, f"{away_team.name} must have 11 players.")
                return redirect(request.path)

            away_lineup, _ = Lineup.objects.get_or_create(match=match, team=away_team)
            away_lineup.players.set(away_ids)
            away_lineup.save()

        return redirect(reverse_lazy('lineup:lineup-detail', kwargs={'match_id': match.id}))

@method_decorator(csrf_exempt, name='dispatch')
class FlutterLineupCreateView(View):
    def post(self, request, match_id):
        try:
            data = json.loads(request.body)
            match = get_object_or_404(Match, pk=match_id)
            team_code = data.get('team_code')
            player_ids = data.get('players', [])
            
            if not team_code:
                return JsonResponse({'error': 'Team code is required'}, status=400)
            
            if len(player_ids) != 11:
                return JsonResponse({'error': 'Must have exactly 11 players'}, status=400)
            
            team = get_object_or_404(Team, code=team_code)
            
            # Check if lineup already exists
            existing_lineup = Lineup.objects.filter(match=match, team=team).first()
            if existing_lineup:
                return JsonResponse({'error': 'Lineup already exists for this team'}, status=400)
            
            # Create new lineup
            lineup = Lineup.objects.create(match=match, team=team)
            
            # Add players
            players = Player.objects.filter(id__in=player_ids, tim=team)
            if players.count() != 11:
                lineup.delete()
                return JsonResponse({'error': 'Invalid players or players do not belong to the team'}, status=400)
            
            lineup.players.set(players)
            
            return JsonResponse({
                'success': True,
                'message': 'Lineup created successfully',
                'lineup_id': str(lineup.id)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class LineupUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Lineup
    form_class = LineupForm
    template_name = 'lineups/lineup_form.html'

    def get_object(self, queryset=None):
        match = Match.objects.get(pk=self.kwargs['match_id'])
        return Lineup.objects.filter(match=match).first()  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = Match.objects.get(pk=self.kwargs['match_id'])
        home_lineup = Lineup.objects.filter(match=match, team__code=match.home_team_code).first()
        away_lineup = Lineup.objects.filter(match=match, team__code=match.away_team_code).first()

        context.update({
            'match': match,
            'home_team': home_lineup.team if home_lineup else None,
            'away_team': away_lineup.team if away_lineup else None,
            'home_selected': [p.id for p in home_lineup.players.all()] if home_lineup else [],
            'away_selected': [p.id for p in away_lineup.players.all()] if away_lineup else [],
            'is_edit': True,
        })
        return context

    def post(self, request, *args, **kwargs):
        match = Match.objects.get(pk=self.kwargs['match_id'])
        home_players_raw = request.POST.get('home_players', '')
        away_players_raw = request.POST.get('away_players', '')

        def parse_ids(raw):
            return [int(pid) for pid in raw.split(',') if pid.strip().isdigit()]

        home_ids = parse_ids(home_players_raw)
        away_ids = parse_ids(away_players_raw)

        home_team = Team.objects.filter(code=match.home_team_code).first()
        away_team = Team.objects.filter(code=match.away_team_code).first()

        if home_team:
            home_lineup, _ = Lineup.objects.get_or_create(match=match, team=home_team)
            home_lineup.players.set(home_ids)

        if away_team:
            away_lineup, _ = Lineup.objects.get_or_create(match=match, team=away_team)
            away_lineup.players.set(away_ids)

        return redirect(reverse_lazy('lineup:lineup-detail', kwargs={'match_id': match.id}))

class FlutterLineupUpdateView(View):
    def put(self, request, lineup_id):
        try:
            data = json.loads(request.body)
            player_ids = data.get('players', [])
            
            if len(player_ids) != 11:
                return JsonResponse({'error': 'Must have exactly 11 players'}, status=400)
            
            lineup = get_object_or_404(Lineup, pk=lineup_id)
            
            # Update players
            players = Player.objects.filter(id__in=player_ids, tim=lineup.team)
            if players.count() != 11:
                return JsonResponse({'error': 'Invalid players or players do not belong to the team'}, status=400)
            
            lineup.players.set(players)
            
            return JsonResponse({
                'success': True,
                'message': 'Lineup updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class LineupDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Lineup
    template_name = 'lineups/lineup_confirm_delete.html'

    def get_object(self, queryset=None):
        match = Match.objects.get(pk=self.kwargs['match_id'])
        return Lineup.objects.filter(match=match).first()

    def post(self, request, *args, **kwargs):
        match = Match.objects.get(pk=self.kwargs['match_id'])
        Lineup.objects.filter(match=match).delete()
        return redirect(reverse_lazy('lineup:lineup-detail', kwargs={'match_id': match.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['match'] = Match.objects.get(pk=self.kwargs['match_id'])
        return context

@method_decorator(csrf_exempt, name='dispatch')
class FlutterLineupDeleteView(View):
    def delete(self, request, lineup_id):
        try:
            lineup = get_object_or_404(Lineup, pk=lineup_id)
            lineup.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Lineup deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

COUNTRY_MAP = {name: code for code, name in COUNTRY_CHOICES}


@method_decorator(csrf_exempt, name='dispatch')
class UploadTeamsView(SuperuserRequiredMixin, View):
    def post(self, request):
        zip_file = request.FILES.get('file')
        if not zip_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        try:
            created, skipped = [], []
            with zipfile.ZipFile(zip_file) as zf:
                for filename in zf.namelist():
                    if not filename.endswith('.json'):
                        continue
                    with zf.open(filename) as f:
                        data = json.load(f)
                        country_name = data.get('negara')
                        if not country_name:
                            skipped.append(filename)
                            continue
                        code = COUNTRY_MAP.get(country_name)
                        if not code:
                            skipped.append(filename)
                            continue
                        team, created_flag = Team.objects.get_or_create(code=code)
                        if created_flag:
                            team.save()
                            created.append(team.name)
                        else:
                            skipped.append(team.name)

            return JsonResponse({
                'status': 'ok',
                'created': created,
                'skipped': skipped
            })
        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UploadPlayersView(SuperuserRequiredMixin, View):
    def post(self, request):
        try:
            # Handle both multipart form data and JSON with base64
            if request.content_type == 'application/json':
                # Base64 JSON format from Flutter
                body = json.loads(request.body)
                base64_file = body.get('file')
                if not base64_file:
                    return JsonResponse({'error': 'No file in JSON'}, status=400)
                zip_bytes = base64.b64decode(base64_file)
                zip_file = io.BytesIO(zip_bytes)
            else:
                # Multipart form data format
                zip_file = request.FILES.get('file')
                if not zip_file:
                    return JsonResponse({'error': 'No file uploaded'}, status=400)

        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': f'Invalid request format: {str(e)}'}, status=400)

        added, skipped, missing_team, invalid = [], [], [], []

        try:
            with zipfile.ZipFile(zip_file) as zf:
                for filename in zf.namelist():
                    if not filename.endswith('.json'):
                        continue

                    with zf.open(filename) as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            invalid.append(filename)
                            continue

                        players = data.get('players', [])
                        if not isinstance(players, list):
                            invalid.append(filename)
                            continue

                        for p in players:
                            required = ['nama', 'tim', 'nomor']
                            if not all(p.get(field) for field in required):
                                skipped.append({
                                    'file': filename,
                                    'reason': f"Missing required fields for {p.get('nama','?')}"
                                })
                                continue

                            team = Team.objects.filter(name=p['tim']).first()
                            if not team:
                                missing_team.append(p['tim'])
                                continue

                            if Player.objects.filter(nomor=p['nomor'], tim=team).exists():
                                skipped.append({
                                    'file': filename,
                                    'reason': f"Duplicate jersey number {p['nomor']} in {team.name}"
                                })
                                continue

                            player = Player.objects.create(
                                nama=p['nama'],
                                asal=p.get('asal', ''),
                                umur=p.get('umur') if p.get('umur') is not None else 0,
                                nomor=p['nomor'],
                                tim=team
                            )
                            added.append(player.nama)

            return JsonResponse({
                'status': 'ok',
                'added_players': added,
                'skipped': skipped,
                'missing_teams': list(set(missing_team)),
                'invalid_files': invalid
            })
        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def get_teams_for_match(request):
    match_id = request.GET.get('match')
    try:
        match = Match.objects.get(pk=match_id)
        teams = Team.objects.filter(code__in=[match.home_team_code, match.away_team_code])
        data = [{'id': t.id, 'name': t.name} for t in teams]
        return JsonResponse({'teams': data})
    except Match.DoesNotExist:
        return JsonResponse({'teams': []})


def get_players_for_team(request):
    team_id = request.GET.get('team')
    try:
        players = Player.objects.filter(tim_id=team_id).order_by('nomor')
        data = [{'id': p.id, 'name': f"{p.nama} (#{p.nomor})"} for p in players]
        return JsonResponse({'players': data})
    except Team.DoesNotExist:
        return JsonResponse({'players': []})

from django.views.decorators.http import require_http_methods

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_team_list(request):
    """GET = list teams, POST = create team"""
    if request.method == "GET":
        teams = Team.objects.all().order_by("name")
        data = [
            {"id": t.id, "code": t.code, "name": t.name}
            for t in teams
        ]
        return JsonResponse({"teams": data})

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name")
            
            if not name:
                return JsonResponse({"error": "Team name is required"}, status=400)
            
            # Look up code from name using COUNTRY_MAP
            code = COUNTRY_MAP.get(name)
            if not code:
                return JsonResponse({"error": "Invalid country name"}, status=400)

            # Check if team already exists
            if Team.objects.filter(code=code).exists():
                return JsonResponse({
                    "error": "Team already exists",
                    "code": code
                }, status=400)

            team = Team.objects.create(code=code)

            return JsonResponse({
                "id": team.id,
                "code": team.code,
                "name": team.name
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def api_team_detail(request, team_id):
    """GET, PUT/PATCH, DELETE on a specific team"""
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": team.id,
            "code": team.code,
            "name": team.name,
            "players": [
                {
                    "id": p.id,
                    "nama": p.nama,
                    "nomor": p.nomor,
                    "umur": p.umur,
                    "asal": p.asal
                }
                for p in team.players.all()
            ]
        })

    elif request.method in ["PUT", "PATCH"]:
        body = json.loads(request.body)
        code = body.get("code")

        if code and code in dict(COUNTRY_CHOICES):
            team.code = code
            team.save()
        else:
            return JsonResponse({"error": "Invalid country code"}, status=400)

        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        team.delete()
        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def api_player_list(request):
    """GET = list players, POST = create player"""
    if request.method == "GET":
        players = Player.objects.all().order_by("nama")
        data = [
            {
                "id": p.id,
                "nama": p.nama,
                "asal": p.asal,
                "umur": p.umur,
                "nomor": p.nomor,
                "team_id": p.tim.id,
                "team_name": p.tim.name,
                "team_code": p.tim.code,
            }
            for p in players
        ]
        return JsonResponse({"players": data})

    elif request.method == "POST":
        try:
            body = json.loads(request.body)

            team_id = body.get("team_id")
            nama = body.get("nama")
            asal = body.get("asal", "")
            umur = body.get("umur", 0)
            nomor = body.get("nomor")

            if not all([team_id, nama, nomor]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            team = Team.objects.get(pk=team_id)

            player = Player.objects.create(
                nama=nama,
                asal=asal,
                umur=umur,
                nomor=nomor,
                tim=team
            )

            return JsonResponse({"id": player.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def api_player_detail(request, player_id):
    """GET, PUT/PATCH, DELETE specific player"""
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": player.id,
            "nama": player.nama,
            "asal": player.asal,
            "umur": player.umur,
            "nomor": player.nomor,
            "team_name": player.tim.name,
        })

    elif request.method in ["PUT", "PATCH"]:
        body = json.loads(request.body)

        player.nama = body.get("nama", player.nama)
        player.asal = body.get("asal", player.asal)
        player.umur = body.get("umur", player.umur)
        player.nomor = body.get("nomor", player.nomor)

        team_name = body.get("team_name")
        if team_name:
            team = Team.objects.filter(name=team_name).first()
            if not team:
                return JsonResponse({"error": "Team not found"}, status=404)
            player.tim = team

        player.save()
        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        player.delete()
        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_update_team(request, team_id):
    """UPDATE - Update a specific team (Flutter API)"""
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found"}, status=404)

    try:
        body = json.loads(request.body)
        code = body.get("code")

        if code and code in dict(COUNTRY_CHOICES):
            team.code = code
            team.save()
            return JsonResponse({
                "success": True,
                "message": "Team updated successfully",
                "team": {
                    "id": team.id,
                    "code": team.code,
                    "name": team.name
                }
            })
        else:
            return JsonResponse({"error": "Invalid country code"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_update_player(request, player_id):
    """UPDATE - Update a specific player (Flutter API)"""
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)

    try:
        body = json.loads(request.body)

        # Update player fields
        if "nama" in body:
            player.nama = body["nama"]
        if "asal" in body:
            player.asal = body["asal"]
        if "umur" in body:
            umur = body["umur"]
            player.umur = umur if umur is not None else 0
        if "nomor" in body:
            player.nomor = body["nomor"]

        # Update team if provided
        if "team_id" in body:
            team_id = body["team_id"]
            try:
                team = Team.objects.get(pk=team_id)
                player.tim = team
            except Team.DoesNotExist:
                return JsonResponse({"error": "Team not found"}, status=404)

        player.save()
        return JsonResponse({
            "success": True,
            "message": "Player updated successfully",
            "player": {
                "id": player.id,
                "nama": player.nama,
                "asal": player.asal,
                "umur": player.umur,
                "nomor": player.nomor,
                "team_id": player.tim.id,
                "team_name": player.tim.name,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_upload_teams(request):
    try:
        # Handle both multipart form data and JSON with base64
        if request.content_type == 'application/json':
            # Base64 JSON format from Flutter
            body = json.loads(request.body)
            base64_file = body.get('file')
            if not base64_file:
                return JsonResponse({'error': 'No file in JSON'}, status=400)
            zip_bytes = base64.b64decode(base64_file)
            zip_file = io.BytesIO(zip_bytes)
        else:
            # Multipart form data format
            zip_file = request.FILES.get('file')
            if not zip_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': f'Invalid request format: {str(e)}'}, status=400)

    created, skipped = [], []

    try:
        with zipfile.ZipFile(zip_file) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.json'):
                    continue

                with zf.open(filename) as f:
                    data = json.load(f)
                    country_name = data.get('negara')

                    if not country_name:
                        skipped.append(filename)
                        continue

                    code = COUNTRY_MAP.get(country_name)
                    if not code:
                        skipped.append(filename)
                        continue

                    # Check if team already exists
                    if Team.objects.filter(code=code).exists():
                        skipped.append({'name': code, 'reason': 'Team already exists'})
                        continue

                    team = Team.objects.create(code=code)
                    created.append(team.name)

        return JsonResponse({
            "status": "ok",
            "created": created,
            "skipped": skipped
        })

    except zipfile.BadZipFile:
        return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_upload_players(request):
    try:
        # Handle both multipart form data and JSON with base64
        if request.content_type == 'application/json':
            # Base64 JSON format from Flutter
            body = json.loads(request.body)
            base64_file = body.get('file')
            if not base64_file:
                return JsonResponse({'error': 'No file in JSON'}, status=400)
            zip_bytes = base64.b64decode(base64_file)
            zip_file = io.BytesIO(zip_bytes)
        else:
            # Multipart form data format
            zip_file = request.FILES.get('file')
            if not zip_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': f'Invalid request format: {str(e)}'}, status=400)

    added, skipped, missing_team, invalid = [], [], [], []

    try:
        with zipfile.ZipFile(zip_file) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.json'):
                    continue

                with zf.open(filename) as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        invalid.append(filename)
                        continue

                    players = data.get('players', [])
                    if not isinstance(players, list):
                        invalid.append(filename)
                        continue

                    for p in players:
                        required = ['nama', 'tim', 'nomor']
                        if not all(p.get(field) for field in required):
                            skipped.append({
                                'file': filename,
                                'reason': f"Missing required fields for {p.get('nama','?')}"
                            })
                            continue

                        team = Team.objects.filter(name=p['tim']).first()
                        if not team:
                            missing_team.append(p['tim'])
                            continue

                        if Player.objects.filter(nomor=p['nomor'], tim=team).exists():
                            skipped.append({
                                'file': filename,
                                'reason': f"Duplicate jersey number {p['nomor']} in {team.name}"
                            })
                            continue

                        player = Player.objects.create(
                            nama=p['nama'],
                            asal=p.get('asal', ''),
                            umur=p.get('umur') if p.get('umur') is not None else 0,
                            nomor=p['nomor'],
                            tim=team
                        )
                        added.append(player.nama)

        return JsonResponse({
            "status": "ok",
            "added": added,
            "skipped": skipped,
            "missing_teams": list(set(missing_team)),
            "invalid_files": invalid,
        })

    except zipfile.BadZipFile:
        return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

