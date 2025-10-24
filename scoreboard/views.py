from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from collections import OrderedDict
from .models import Match
from collections import OrderedDict
from .models import Match
from .forms import MatchForm
from django.utils import timezone
from django.db.models.functions import TruncDate
from forum.models import Forum
from django.contrib import messages
from prediction.models import Prediction
from django.http import HttpResponseForbidden

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
        return HttpResponseForbidden("You do not have permission to add matches.")
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            
            Forum.objects.create(
                match=match,
                nama= "About " + match.home_team + " vs " + match.away_team,
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
        return HttpResponseForbidden("You do not have permission to update scores.")
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
        return HttpResponseForbidden("You do not have permission to delete matches.")
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        match.delete()
        messages.success(request, "Pertandingan berhasil dihapus.")
    
    return redirect('scoreboard:scoreboard_list')
