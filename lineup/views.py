import io
import json
import zipfile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy,reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Team, Player, Lineup, COUNTRY_CHOICES
from .forms import LineupForm, TeamForm, PlayerInlineFormSet
from scoreboard.models import Match
from django.contrib import messages
from django.forms import modelform_factory
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django import forms
from django.shortcuts import get_object_or_404
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        if self.request.POST:
            context['player_formset'] = PlayerInlineFormSet(self.request.POST, instance=team)
        else:
            context['player_formset'] = PlayerInlineFormSet(instance=team)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        player_formset = context['player_formset']

        if player_formset.is_valid():
            self.object = form.save()
            player_formset.instance = self.object
            player_formset.save()
            messages.success(self.request, "Team and players updated successfully!")
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Please correct errors in player fields.")
            return self.form_invalid(form)

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
        zip_file = request.FILES.get('file')
        if not zip_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

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
                            required_fields = ['nama', 'tim', 'nomor']
                            if not all(field in p and p[field] not in (None, '') for field in required_fields):
                                skipped.append({
                                    'file': filename,
                                    'reason': f"Missing required fields in player {p.get('nama', '(unknown)')}"
                                })
                                continue

                            team_name = p.get('tim')
                            team = Team.objects.filter(name=team_name).first()
                            if not team:
                                missing_team.append(team_name)
                                continue

                            if Player.objects.filter(nomor=p['nomor'], tim=team).exists():
                                skipped.append({
                                    'file': filename,
                                    'reason': f"Duplicate jersey number {p['nomor']} in team {team.name}"
                                })
                                continue

                            try:
                                player = Player.objects.create(
                                    nama=p['nama'],
                                    asal=p.get('asal', ''),
                                    umur=p.get('umur') or 0,
                                    nomor=p['nomor'],
                                    tim=team
                                )
                                added.append(player.nama)
                            except Exception as e:
                                skipped.append({
                                    'file': filename,
                                    'reason': str(e)
                                })

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
