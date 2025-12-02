from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Statistik
from .forms import StatistikForm
from scoreboard.models import Match

def statistik_json(request, match_id):
    """API untuk Flutter - Get statistik dalam format JSON"""
    match = get_object_or_404(Match, id=match_id)
    statistik = Statistik.objects.filter(match=match).first()
    
    if not statistik:
        return JsonResponse({'error': 'Statistik not found'}, status=404)
    
    data = {
        'id': str(statistik.id),
        'match_id': str(match.id),
        'home_team': match.home_team,
        'away_team': match.away_team,
        'home_score': match.home_score,
        'away_score': match.away_score,
        
        # SESUAIKAN DENGAN MODEL YANG ADA
        'home_shots': statistik.shoot_home,
        'away_shots': statistik.shoot_away,
        'home_shots_on_target': statistik.on_target_home,
        'away_shots_on_target': statistik.on_target_away,
        'home_corners': statistik.corner_home,
        'away_corners': statistik.corner_away,
        'home_yellow_cards': statistik.yellow_card_home,
        'away_yellow_cards': statistik.yellow_card_away,
        'home_red_cards': statistik.red_card_home,
        'away_red_cards': statistik.red_card_away,
        'home_offsides': statistik.offside_home,
        'away_offsides': statistik.offside_away,
        'home_passes': statistik.pass_home,
        'away_passes': statistik.pass_away,
        
        # Ball possession sebagai persen (pastikan di model sudah dalam bentuk persen)
        'home_possession': float(statistik.ball_possession_home),
        'away_possession': float(statistik.ball_possession_away),
        
        'match_date': match.match_date.isoformat(),
        'stadium': match.stadium,
    }
    
    return JsonResponse(data)

def statistik_list_json(request):
    """API untuk Flutter - Get semua statistik"""
    statistik_list = Statistik.objects.select_related('match').all()
    
    data = []
    for statistik in statistik_list:
        match = statistik.match
        data.append({
            'id': str(statistik.id),
            'match_id': str(match.id),
            'home_team': match.home_team,
            'away_team': match.away_team,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'home_shots': statistik.shoot_home,
            'away_shots': statistik.shoot_away,
            'home_shots_on_target': statistik.on_target_home,
            'away_shots_on_target': statistik.on_target_away,
            'home_corners': statistik.corner_home,
            'away_corners': statistik.corner_away,
            'home_yellow_cards': statistik.yellow_card_home,
            'away_yellow_cards': statistik.yellow_card_away,
            'home_red_cards': statistik.red_card_home,
            'away_red_cards': statistik.red_card_away,
            'home_offsides': statistik.offside_home,
            'away_offsides': statistik.offside_away,
            'home_passes': statistik.pass_home,
            'away_passes': statistik.pass_away,
            'home_possession': float(statistik.ball_possession_home),  # sebagai persen
            'away_possession': float(statistik.ball_possession_away),  # sebagai persen
            'match_date': match.match_date.isoformat(),
            'stadium': match.stadium,
        })
    
    return JsonResponse(data, safe=False)

def add_statistik(request, match_id):
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        return redirect('statistik:statistik_display', match_id=match.id)
    
    #VALIDASI STATUS MATCH
    if match.status not in ['live', 'finished']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Tidak bisa menambah statistik untuk pertandingan dengan status: {match.status}. Hanya pertandingan LIVE atau FINISHED yang bisa memiliki statistik.'
            })
        messages.error(request, f'Tidak bisa menambah statistik untuk pertandingan dengan status: {match.status}')
        return redirect('statistik:statistik_display', match_id=match.id)
    
    # Cek apakah sudah ada statistik
    existing_statistik = Statistik.objects.filter(match=match).first()
    if existing_statistik:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Statistik untuk pertandingan ini sudah ada!'
            })
        messages.warning(request, 'Statistik untuk pertandingan ini sudah ada!')
        return redirect('statistik:statistik_display', match_id=match.id)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            try:
                data = json.loads(request.body)
                form = StatistikForm(data)
                if form.is_valid():
                    statistik = form.save(commit=False)
                    statistik.match = match
                    statistik.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Statistik berhasil ditambahkan!',
                        'redirect_url': f'/statistik/{match.id}/'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Data tidak valid!',
                        'errors': form.errors
                    })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Terjadi kesalahan: {str(e)}'
                })
        else:
            # Normal form submission
            form = StatistikForm(request.POST)
            if form.is_valid():
                statistik = form.save(commit=False)
                statistik.match = match
                statistik.save()
                messages.success(request, 'Statistik berhasil ditambahkan!')
                return redirect('statistik:statistik_display', match_id=match.id)
            else:
                messages.error(request, 'Terjadi kesalahan. Periksa data Anda!')
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
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to update statistics.")
        return redirect('statistik:statistik_display', match_id=match_id)
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = get_object_or_404(Statistik, match=match)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            try:
                data = json.loads(request.body)
                form = StatistikForm(data, instance=statistik)
                if form.is_valid():
                    form.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Statistik berhasil diupdate!',
                        'redirect_url': f'/statistik/{match.id}/'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Data tidak valid!',
                        'errors': form.errors
                    })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Terjadi kesalahan: {str(e)}'
                })
        else:
            # Normal form submission
            form = StatistikForm(request.POST, instance=statistik)
            if form.is_valid():
                form.save()
                messages.success(request, 'Statistik berhasil diupdate!')
                return redirect('statistik:statistik_display', match_id=match.id)
            else:
                messages.error(request, 'Terjadi kesalahan. Periksa data Anda!')
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
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to delete statistik.")
        return redirect('statistik:statistik_display', match_id=match_id)
    from scoreboard.models import Match
    match = get_object_or_404(Match, id=match_id)
    statistik = get_object_or_404(Statistik, match=match)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            try:
                statistik.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Statistik berhasil dihapus!',
                    'redirect_url': '/scoreboard/'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Terjadi kesalahan: {str(e)}'
                })
        else:
            # Normal form submission
            statistik.delete()
            messages.success(request, 'Statistik berhasil dihapus!')
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