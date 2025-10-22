from django.shortcuts import render, redirect, get_object_or_404
from .models import Statistik
from .forms import StatistikForm

def add_statistik(request):
    if request.method == 'POST':
        form = StatistikForm(request.POST)
        if form.is_valid():
            statistik = form.save()
            return redirect('statistik:statistik_display', match_id=statistik.match.id)
    else:
        form = StatistikForm()
    
    return render(request, 'statistik/add_statistik.html', {'form': form})

def add_statistik_for_match(request, match_id):
    """Add statistik untuk match tertentu dari scoreboard"""
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    
    # Cek apakah sudah ada statistik
    existing_statistik = Statistik.objects.filter(match=match).first()
    if existing_statistik:
        return redirect('statistik:statistik_display', match_id=match.id)
    
    if request.method == 'POST':
        form = StatistikForm(request.POST)
        if form.is_valid():
            statistik = form.save(commit=False)
            statistik.match = match  # Set match dari URL
            statistik.save()
            return redirect('statistik:statistik_display', match_id=match.id)
    else:
        # Pre-fill form dengan match
        form = StatistikForm(initial={'match': match})
    
    context = {
        'form': form,
        'match': match
    }
    return render(request, 'statistik/add_statistik.html', context)

def statistik_display(request, match_id):
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = get_object_or_404(Statistik, match=match)
    
    context = {
        'match': match,
        'statistik': statistik,
    }
    return render(request, 'statistik/statistik_display.html', context)