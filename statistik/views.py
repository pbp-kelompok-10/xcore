from django.shortcuts import render, redirect, get_object_or_404
from .models import Statistik
from .forms import StatistikForm
from scoreboard.views import Match

def add_statistik(request):
    if request.method == 'POST':
        form = StatistikForm(request.POST)
        if form.is_valid():
            statistik = form.save()
            return redirect('statistik:statistik_display', match_id=statistik.match_id)
    else:
        form = StatistikForm()
    
    return render(request, 'statistik/add_statistik.html', {'form': form})

def statistik_display(request, match_id):
    # Pastikan match dengan ID itu ada
    match = get_object_or_404(Match, id=match_id)

    # Coba ambil Statistik, tapi jangan error kalau gak ada
    statistik = Statistik.objects.filter(match=match).first()

    # Kalau belum ada statistik, kirim nilai default kosong
    if not statistik:
        context = {
            'match': match,
            'statistik': None,
            'pass_home_percentage': 0,
            'pass_away_percentage': 0,
            'shoot_home_percentage': 0,
            'shoot_away_percentage': 0,
            'on_target_home_percentage': 0,
            'on_target_away_percentage': 0,
        }
        return render(request, 'statistik/statistik_display.html', context)

    # Kalau statistik ada, hitung persentase
    total_passes = statistik.pass_home + statistik.pass_away
    total_shots = statistik.shoot_home + statistik.shoot_away
    total_on_target = statistik.on_target_home + statistik.on_target_away

    context = {
        'match': match,
        'statistik': statistik,
        'pass_home_percentage': (statistik.pass_home / total_passes * 100) if total_passes > 0 else 50,
        'pass_away_percentage': (statistik.pass_away / total_passes * 100) if total_passes > 0 else 50,
        'shoot_home_percentage': (statistik.shoot_home / total_shots * 100) if total_shots > 0 else 50,
        'shoot_away_percentage': (statistik.shoot_away / total_shots * 100) if total_shots > 0 else 50,
        'on_target_home_percentage': (statistik.on_target_home / total_on_target * 100) if total_on_target > 0 else 50,
        'on_target_away_percentage': (statistik.on_target_away / total_on_target * 100) if total_on_target > 0 else 50,
    }

    return render(request, 'statistik/statistik_display.html', context)