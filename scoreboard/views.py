from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Match
from .forms import MatchForm

def scoreboard_list(request):
    matches = Match.objects.all().order_by('-match_date')
    return render(request, 'scoreboard_list.html', {'matches': matches})

def admin_check(user):
    return user.is_superuser

# @user_passes_test(admin_check)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
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