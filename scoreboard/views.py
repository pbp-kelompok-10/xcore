import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from collections import OrderedDict
from .models import Match
from collections import OrderedDict
from .models import Match
from .forms import MatchForm
from forum.views import create_forum_for_match, delete_forum
from django.utils import timezone
from django.db.models.functions import TruncDate
from forum.models import Forum
from django.contrib import messages
from prediction.models import Prediction
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_match_json(request):
    if request.method == "POST":
        data = json.loads(request.body)

        match = Match.objects.create(
            home_team_code=data['home_team_code'],
            away_team_code=data['away_team_code'],
            match_date=data['match_date'],
            stadium=data['stadium'],
            round=data.get('round'),
            group=data.get('group'),
            status=data.get('status', 'upcoming'),
        )
        
        return JsonResponse({
            "status": "success",
            "id": str(match.id)
        })

    return JsonResponse({"error": "POST only"}, status=400)


def scoreboard_json(request):
    matches = Match.objects.all().order_by('match_date')

    data = []
    for match in matches:
        data.append({
            "id": str(match.id),
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_team_code": match.home_team_code,
            "away_team_code": match.away_team_code,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "match_date": match.match_date,
            "stadium": match.stadium,
            "round": match.round,
            "group": match.group,
            "status": match.status,
        })

    return JsonResponse(data, safe=False)

def scoreboard_list(request):
    matches = Match.objects.all().order_by('match_date')
    
    matches_by_date = OrderedDict()
    for match in matches:
        match_date = match.match_date.date() 
        if match_date not in matches_by_date:
            matches_by_date[match_date] = []
        matches_by_date[match_date].append(match)
    
    context = {
        'matches_by_date': matches_by_date
    }
    return render(request, 'scoreboard_list.html', context)


def add_match(request):
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to add matches.")
        return redirect('scoreboard:scoreboard_list')
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            
            Forum.objects.create(
                match=match,
                nama="About " + match.home_team + " vs " + match.away_team,
            )

            Prediction.objects.create(
                match=match,
            )
            messages.success(request, 'Pertandingan berhasil ditambahkan!')
            return redirect('scoreboard:scoreboard_list')
    else:
        form = MatchForm()
    
    return render(request, 'add_match.html', {'form': form})


def update_score(request, match_id):
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to update scores.")
        return redirect('scoreboard:scoreboard_list')
    match = get_object_or_404(Match, id=match_id)
    
    if request.method == "POST":
        match.home_score = request.POST.get('home_score')
        match.away_score = request.POST.get('away_score')
        match.status = request.POST.get('status')
        match.round = request.POST.get('round')
        match.group = request.POST.get('group')
        match.stadium = request.POST.get('stadium')
        match.save()
        messages.success(request, 'Pertandingan berhasil diperbarui!')
        return redirect('scoreboard:scoreboard_list')

    return render(request, 'update_score.html', {'match': match})

def delete_match(request, match_id):
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to delete matches.")
        return redirect('scoreboard:scoreboard_list')
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        match.delete()
        messages.success(request, "Pertandingan berhasil dihapus.")
        
    delete_forum(request, match_id)
    
    return redirect('scoreboard:scoreboard_list')
