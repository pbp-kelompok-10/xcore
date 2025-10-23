from django.shortcuts import render, redirect, get_object_or_404
from .models import Statistik
from .forms import StatistikForm

def add_statistik(request, match_id):
    """CREATE - Tambah statistik baru"""
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
            statistik.match = match
            statistik.save()
            return redirect('statistik:statistik_display', match_id=match.id)
    else:
        form = StatistikForm(initial={'match': match})
    
    context = {
        'form': form,
        'match': match,
        'action': 'Tambah'
    }
    return render(request, 'statistik/statistik_form.html', context)

def update_statistik(request, match_id):
    """UPDATE - Edit statistik yang sudah ada"""
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = get_object_or_404(Statistik, match=match)
    
    if request.method == 'POST':
        form = StatistikForm(request.POST, instance=statistik)
        if form.is_valid():
            form.save()
            return redirect('statistik:statistik_display', match_id=match.id)
    else:
        form = StatistikForm(instance=statistik)
    
    context = {
        'form': form,
        'match': match,
        'statistik': statistik,
        'action': 'Update'
    }
    return render(request, 'statistik/statistik_form.html', context)

def delete_statistik(request, match_id):
    """DELETE - Hapus statistik"""
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = get_object_or_404(Statistik, match=match)
    
    if request.method == 'POST':
        statistik.delete()
        return redirect('scoreboard:scoreboard_list')
    
    context = {
        'match': match,
        'statistik': statistik
    }
    return render(request, 'statistik/delete_statistik.html', context)

def statistik_display(request, match_id):
    """READ - Tampilkan statistik"""
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = Statistik.objects.filter(match=match).first()
    
    context = {
        'match': match,
        'statistik': statistik,
    }
    return render(request, 'statistik/statistik_display.html', context)