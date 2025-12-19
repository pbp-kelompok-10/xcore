from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Statistik
from .forms import StatistikForm
from scoreboard.models import Match
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# ========== MIXINS ==========
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

# ========== API ENDPOINTS (Flutter) ==========

@method_decorator(csrf_exempt, name='dispatch')
class FlutterStatistikDetailView(View):
    """API untuk Flutter - Get statistik dalam format JSON"""
    def get(self, request, match_id):
        try:
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
                'home_possession': float(statistik.ball_possession_home),
                'away_possession': float(statistik.ball_possession_away),
                'match_date': match.match_date.isoformat(),
                'stadium': match.stadium,
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FlutterStatistikCreateView(View):
    def post(self, request):
        print("=== FLUTTER CREATE STATISTIK ===")
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        
        try:
            # Coba ambil dari request.POST (form-urlencoded)
            if request.POST:
                data = request.POST
                print(f"Data from request.POST: {dict(data)}")
            else:
                # Coba parse JSON
                try:
                    data = json.loads(request.body)
                    print(f"Data from JSON: {data}")
                except:
                    data = {}
            
            # Get match object
            try:
                match_id = data.get('match')
                if not match_id:
                    return JsonResponse({
                        "status": False,
                        "message": "Match ID is required"
                    }, status=400)
                    
                match = Match.objects.get(id=match_id)
                print(f"Found match: {match.home_team} vs {match.away_team}")
                
            except Match.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "message": f"Match with id {match_id} not found"
                }, status=404)
            
            # Check if statistik already exists
            if Statistik.objects.filter(match=match).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Statistik already exists for this match"
                }, status=400)
            
            # Create new statistik dengan konversi tipe yang aman
            try:
                statistik = Statistik.objects.create(
                    match=match,
                    pass_home=int(data.get('home_passes', 0)),
                    pass_away=int(data.get('away_passes', 0)),
                    shoot_home=int(data.get('home_shots', 0)),
                    shoot_away=int(data.get('away_shots', 0)),
                    on_target_home=int(data.get('home_shots_on_target', 0)),
                    on_target_away=int(data.get('away_shots_on_target', 0)),
                    ball_possession_home=float(data.get('home_possession', 50.0)),
                    ball_possession_away=float(data.get('away_possession', 50.0)),
                    red_card_home=int(data.get('home_red_cards', 0)),
                    red_card_away=int(data.get('away_red_cards', 0)),
                    yellow_card_home=int(data.get('home_yellow_cards', 0)),
                    yellow_card_away=int(data.get('away_yellow_cards', 0)),
                    offside_home=int(data.get('home_offsides', 0)),
                    offside_away=int(data.get('away_offsides', 0)),
                    corner_home=int(data.get('home_corners', 0)),
                    corner_away=int(data.get('away_corners', 0)),
                )
                
                print(f"Statistik created: {statistik.id}")
                
                return JsonResponse({
                    "status": True,
                    "message": "Statistik created successfully",
                    "statistik_id": str(statistik.id)
                }, status=201)
                
            except ValueError as e:
                return JsonResponse({
                    "status": False,
                    "message": f"Invalid data type: {str(e)}"
                }, status=400)
            
        except Exception as e:
            print(f"Error creating statistik: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": False,
                "message": f"Error creating statistik: {str(e)}"
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FlutterStatistikUpdateView(View):
    """Update statistik dari Flutter"""
    def put(self, request, match_id):
        print("=== FLUTTER UPDATE STATISTIK ===")
        print(f"Match ID: {match_id}")
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Body raw: {request.body}")
        
        try:
            # PARSE JSON DATA
            data = json.loads(request.body)
            print(f"Parsed JSON data: {data}")
            print(f"Type of data: {type(data)}")
            
            # Get statistik by match_id
            try:
                statistik = Statistik.objects.get(match_id=match_id)
                print(f"Found statistik: {statistik.id}")
            except Statistik.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "message": f"Statistik not found for match {match_id}"
                }, status=404)
            
            # Update fields - dengan error handling untuk tipe data
            try:
                # Home team stats
                if 'home_passes' in data:
                    statistik.pass_home = int(data['home_passes'])
                if 'away_passes' in data:
                    statistik.pass_away = int(data['away_passes'])
                if 'home_shots' in data:
                    statistik.shoot_home = int(data['home_shots'])
                if 'away_shots' in data:
                    statistik.shoot_away = int(data['away_shots'])
                if 'home_shots_on_target' in data:
                    statistik.on_target_home = int(data['home_shots_on_target'])
                if 'away_shots_on_target' in data:
                    statistik.on_target_away = int(data['away_shots_on_target'])
                if 'home_possession' in data:
                    statistik.ball_possession_home = float(data['home_possession'])
                if 'away_possession' in data:
                    statistik.ball_possession_away = float(data['away_possession'])
                if 'home_red_cards' in data:
                    statistik.red_card_home = int(data['home_red_cards'])
                if 'away_red_cards' in data:
                    statistik.red_card_away = int(data['away_red_cards'])
                if 'home_yellow_cards' in data:
                    statistik.yellow_card_home = int(data['home_yellow_cards'])
                if 'away_yellow_cards' in data:
                    statistik.yellow_card_away = int(data['away_yellow_cards'])
                if 'home_offsides' in data:
                    statistik.offside_home = int(data['home_offsides'])
                if 'away_offsides' in data:
                    statistik.offside_away = int(data['away_offsides'])
                if 'home_corners' in data:
                    statistik.corner_home = int(data['home_corners'])
                if 'away_corners' in data:
                    statistik.corner_away = int(data['away_corners'])
                
                statistik.save()
                
                print(f"Statistik updated: {statistik.id}")
                
                return JsonResponse({
                    "status": True,
                    "message": "Statistik updated successfully"
                }, status=200)
                
            except ValueError as e:
                print(f"ValueError: {e}")
                return JsonResponse({
                    "status": False,
                    "message": f"Invalid data type: {str(e)}"
                }, status=400)
            except Exception as e:
                print(f"Error updating fields: {e}")
                return JsonResponse({
                    "status": False,
                    "message": f"Error updating fields: {str(e)}"
                }, status=400)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({
                "status": False,
                "message": f"Invalid JSON data: {str(e)}"
            }, status=400)
        except Exception as e:
            print(f"General error in update statistik: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": False,
                "message": f"Error updating statistik: {str(e)}"
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FlutterStatistikDeleteView(View):
    """Delete statistik dari Flutter"""
    def delete(self, request, match_id):
        try:
            print(f"Flutter delete statistik - Match ID: {match_id}")
            
            # Get statistik by match_id
            try:
                statistik = Statistik.objects.get(match_id=match_id)
            except Statistik.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "message": f"Statistik not found for match {match_id}"
                }, status=404)
            
            statistik.delete()
            
            print(f"Statistik deleted successfully for match {match_id}")
            
            return JsonResponse({
                "status": True,
                "message": "Statistik deleted successfully"
            }, status=200)
            
        except Exception as e:
            print(f"Error deleting statistik: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": False,
                "message": f"Error deleting statistik: {str(e)}"
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FlutterStatistikListView(View):
    """Get semua statistik untuk Flutter"""
    def get(self, request):
        try:
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
                    'home_possession': float(statistik.ball_possession_home),
                    'away_possession': float(statistik.ball_possession_away),
                    'match_date': match.match_date.isoformat(),
                    'stadium': match.stadium,
                })
            
            return JsonResponse(data, safe=False)
            
        except Exception as e:
            print(f"Error getting statistik list: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


# ========== WEB VIEWS (Existing Django views) ==========

def add_statistik(request, match_id):
    """Tambah statistik - WEB"""
    match = get_object_or_404(Match, id=match_id)
    
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        return redirect('statistik:statistik_display', match_id=match.id)
    
    # VALIDASI STATUS MATCH
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
    """Delete statistik - WEB"""
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "You do not have permission to delete statistik.")
        return redirect('statistik:statistik_display', match_id=match_id)
    
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
    """READ - Tampilkan statistik - WEB"""
    match = get_object_or_404(Match, id=match_id)
    statistik = Statistik.objects.filter(match=match).first()
    
    context = {
        'match': match,
        'statistik': statistik,
    }
    return render(request, 'statistik/statistik_display.html', context)


def statistik_json(request, match_id):
    """API legacy - Get statistik dalam format JSON"""
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
        'home_possession': float(statistik.ball_possession_home),
        'away_possession': float(statistik.ball_possession_away),
        'match_date': match.match_date.isoformat(),
        'stadium': match.stadium,
    }
    
    return JsonResponse(data)


def statistik_list_json(request):
    """API legacy - Get semua statistik"""
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
            'home_possession': float(statistik.ball_possession_home),
            'away_possession': float(statistik.ball_possession_away),
            'match_date': match.match_date.isoformat(),
            'stadium': match.stadium,
        })
    
    return JsonResponse(data, safe=False)


# ========== USER INFO ENDPOINTS ==========

@method_decorator(csrf_exempt, name='dispatch')
class GetUserInfoView(View):
    """Get current user information including admin status"""
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": False,
                "message": "User not authenticated"
            }, status=401)
        
        user = request.user
        return JsonResponse({
            "status": True,
            "user": {
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "is_admin": user.is_staff or user.is_superuser
            }
        })
    