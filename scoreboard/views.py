from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from collections import OrderedDict
from .models import Match
from .forms import MatchForm
from forum.models import Forum
from forum.models import Forum
from django.utils import timezone
from django.db.models.functions import TruncDate

def scoreboard_list(request):
    # Group matches by date
    matches = Match.objects.all().order_by('match_date')
    
    # Group matches by date
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

def admin_check(user):
    return user.is_superuser

# @user_passes_test(admin_check)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            
            Forum.objects.create(
                match=match,
                nama= "About " + match.home_team + " vs " + match.away_team,
            )
            
            return redirect('scoreboard:scoreboard_list')
    else:
        form = MatchForm()
    
    return render(request, 'add_match.html', {'form': form})

# @user_passes_test(admin_check)
def update_score(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('scoreboard:scoreboard_list')
    else:
        form = MatchForm(instance=match)
        
    return render(request, 'scoreboard/update_score.html', {'form': form, 'match': match})