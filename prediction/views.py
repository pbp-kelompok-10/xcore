from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from scoreboard.models import Match
from .models import Prediction, Vote
from django.utils import timezone

def prediction_list(request):
    upcoming_predictions = Prediction.objects.filter(match__status='upcoming')
    live_predictions = Prediction.objects.filter(match__status='live')
    finished_predictions = Prediction.objects.filter(match__status='finished')

    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(user=request.user)
        vote_map = {v.prediction_id: v for v in user_votes}
        # Tambahkan atribut `user_vote` ke setiap prediction
        for p in list(upcoming_predictions) + list(live_predictions) + list(finished_predictions):
            p.user_vote = vote_map.get(p.id)
    else:
        for p in list(upcoming_predictions) + list(live_predictions) + list(finished_predictions):
            p.user_vote = None

    return render(request, 'prediction_center.html', {
        'upcoming_predictions': upcoming_predictions,
        'live_predictions': live_predictions,
        'finished_predictions': finished_predictions,
    })

@login_required(login_url='/login')
def submit_vote(request):
    if request.method == "POST":
        prediction_id = request.POST.get("prediction_id")
        choice = request.POST.get("choice")

        if not prediction_id or not choice:
            return JsonResponse({"status": "error", "message": "Missing required parameters"})

        try:
            prediction = Prediction.objects.get(id=prediction_id)
        except Prediction.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Prediction not found"})
        
        if not prediction.is_voting_open():
            return JsonResponse({
                "status": "error", 
                "message": "Voting sudah ditutup! Deadline 2 jam sebelum match dimulai."
            })

        if Vote.objects.filter(user=request.user, prediction=prediction).exists():
            return JsonResponse({
                "status": "error", 
                "message": "Kamu sudah vote! Mau ubah vote? Klik 'My Votes'"
            })

        vote = Vote.objects.create(
            user=request.user,
            prediction=prediction,
            choice=choice.lower().strip(),
            voted_at=timezone.now()
        )

        choice = choice.lower().strip()
        if "home" in choice:
            prediction.votes_home_team += 1
        elif "away" in choice:
            prediction.votes_away_team += 1
        
        prediction.save()
        
        return JsonResponse({
            "status": "success",
            "vote_id": str(vote.id),
            "voted_at": vote.voted_at.isoformat(),
            "votes_home_team": prediction.votes_home_team,
            "votes_away_team": prediction.votes_away_team,
            "home_percentage": float(prediction.home_percentage),
            "away_percentage": float(prediction.away_percentage)
        })

    return JsonResponse({"status": "error", "message": "Invalid request method"})


@login_required
def my_votes(request):
    """READ - User lihat history vote sendiri"""
    votes = Vote.objects.filter(user=request.user).select_related('prediction__match').order_by('-voted_at')
    
    context = {
        'votes': votes
    }
    return render(request, 'my_votes.html', context)


@login_required
def update_vote(request, vote_id=None):
    """UPDATE - User ubah vote sendiri (handle both AJAX and HTML form)"""
    
    # Handle AJAX request (dari modal)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or not vote_id:
        if request.method != 'POST':
            return JsonResponse({
                'status': 'error',
                'message': 'Method not allowed'
            }, status=405)
        
        # Ambil vote_id dari POST body untuk AJAX
        vote_id = request.POST.get('vote_id') or vote_id
        choice = request.POST.get('choice')  # 'home' atau 'away'
        
        if not vote_id or not choice:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            })
        
        try:
            vote = get_object_or_404(Vote, id=vote_id, user=request.user)
            
            # Cek apakah masih bisa diubah
            if not vote.can_modify():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Voting sudah ditutup! Tidak bisa ubah vote lagi.'
                })
            
            prediction = vote.prediction
            
            # Kurangi vote lama
            old_choice = vote.choice.lower().strip()
            if "home" in old_choice:
                prediction.votes_home_team = max(0, prediction.votes_home_team - 1)
            elif "away" in old_choice:
                prediction.votes_away_team = max(0, prediction.votes_away_team - 1)
            
            # Tambah vote baru
            new_choice = choice.lower().strip()
            if new_choice == 'home' or 'home' in new_choice:
                prediction.votes_home_team += 1
                vote.choice = 'home'
            elif new_choice == 'away' or 'away' in new_choice:
                prediction.votes_away_team += 1
                vote.choice = 'away'
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid choice'
                })
            
            vote.voted_at = timezone.now()
            vote.save()
            prediction.save()
            
            return JsonResponse({
                'status': 'success',
                'vote_id': str(vote.id),
                'voted_at': vote.voted_at.isoformat(),
                'votes_home_team': prediction.votes_home_team,
                'votes_away_team': prediction.votes_away_team,
                'home_percentage': float(prediction.home_percentage),
                'away_percentage': float(prediction.away_percentage)
            })
            
        except Vote.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Vote tidak ditemukan'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Terjadi kesalahan: {str(e)}'
            })
    
    # Handle HTML form request (dari halaman update_vote.html)
    vote = get_object_or_404(Vote, id=vote_id, user=request.user)
    
    if not vote.can_modify():
        messages.error(request, "Voting sudah ditutup! Tidak bisa ubah vote lagi.")
        return redirect('prediction:my_votes')
    
    if request.method == 'POST':
        old_choice = vote.choice.lower().strip()
        new_choice = request.POST.get('choice').lower().strip()
        
        prediction = vote.prediction
        
        # Kurangi vote lama
        if "home" in old_choice:
            prediction.votes_home_team = max(0, prediction.votes_home_team - 1)
        elif "away" in old_choice:
            prediction.votes_away_team = max(0, prediction.votes_away_team - 1)
        
        # Tambah vote baru
        if "home" in new_choice:
            prediction.votes_home_team += 1
            vote.choice = 'home'
        elif "away" in new_choice:
            prediction.votes_away_team += 1
            vote.choice = 'away'
        
        vote.voted_at = timezone.now()
        vote.save()
        prediction.save()
        
        messages.success(request, "Vote berhasil diubah!")
        return redirect('prediction:my_votes')
    
    context = {
        'vote': vote
    }
    return render(request, 'update_vote.html', context)


@login_required
def delete_vote(request, vote_id):
    """DELETE - User hapus vote sendiri (sebelum deadline)"""
    vote = get_object_or_404(Vote, id=vote_id, user=request.user)

    if request.method != "POST":
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed. Use POST to delete a vote.'
        }, status=405)
    
    if not vote.can_modify():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': 'Voting sudah ditutup! Tidak bisa hapus vote lagi.'
            })
        messages.error(request, "Voting sudah ditutup! Tidak bisa hapus vote lagi.")
        return redirect('prediction:my_votes')
    
    if request.method == 'POST':
        prediction = vote.prediction
        choice = vote.choice.lower().strip()
        
        if "home" in choice:
            prediction.votes_home_team = max(0, prediction.votes_home_team - 1)
        elif "away" in choice:
            prediction.votes_away_team = max(0, prediction.votes_away_team - 1)
        
        prediction.save()
        
        vote.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'status': 'success',
                'message': 'Vote berhasil dihapus!',
                'prediction_id': str(prediction.id),
                'votes_home_team': prediction.votes_home_team,
                'votes_away_team': prediction.votes_away_team,
                'home_percentage': float(prediction.home_percentage),
                'away_percentage': float(prediction.away_percentage)
            })
        
        messages.success(request, "Vote berhasil dihapus!")
        return redirect('prediction:my_votes')