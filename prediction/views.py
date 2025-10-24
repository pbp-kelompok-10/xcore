from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from scoreboard.models import Match
from .models import Prediction, Vote



def prediction_list(request):
    """Halaman utama untuk user melihat semua predictions"""
    predictions = Prediction.objects.select_related('match').all()
    
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user).select_related("prediction")
    else:
        votes = Vote.objects.none()  # Empty queryset untuk user yang belum login
    
    upcoming_predictions = predictions.filter(match__status='upcoming')
    live_predictions = predictions.filter(match__status='live')
    finished_predictions = predictions.filter(match__status='finished')

    context = {
        'upcoming_predictions': upcoming_predictions,
        'live_predictions': live_predictions,
        'finished_predictions': finished_predictions,
        'votes': votes,
    }

    return render(request, 'prediction_center.html', context)


@login_required(login_url='/login')
def submit_vote(request):
    if request.method == "POST":
        prediction_id = request.POST.get("prediction_id")
        choice = request.POST.get("choice")

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

        Vote.objects.create(user=request.user, prediction=prediction, choice=choice)

        choice = choice.lower().strip()
        if "home" in choice:
            prediction.votes_home_team += 1
        elif "away" in choice:
            prediction.votes_away_team += 1
        
        prediction.save()
        
        return JsonResponse({
            "status": "success",
            "home": {
                "team": prediction.match.home_team,
                "votes": prediction.votes_home_team,
                "percent": prediction.home_percentage
            },
            "away": {
                "team": prediction.match.away_team,
                "votes": prediction.votes_away_team,
                "percent": prediction.away_percentage
            }
        })

    return JsonResponse({"status": "error", "message": "Invalid request"})


@login_required
def my_votes(request):
    """READ - User lihat history vote sendiri"""
    votes = Vote.objects.filter(user=request.user).select_related('prediction__match').order_by('-voted_at')
    
    context = {
        'votes': votes
    }
    return render(request, 'my_votes.html', context)


@login_required
def update_vote(request, vote_id):
    """UPDATE - User ubah vote sendiri (sebelum deadline)"""
    vote = get_object_or_404(Vote, id=vote_id, user=request.user)
    
    if not vote.can_modify():
        messages.error(request, "Voting sudah ditutup! Tidak bisa ubah vote lagi.")
        return redirect('prediction:my_votes')
    
    if request.method == 'POST':
        old_choice = vote.choice.lower().strip()
        new_choice = request.POST.get('choice').lower().strip()
        
        prediction = vote.prediction
        
        if "home" in old_choice:
            prediction.votes_home_team -= 1
        elif "away" in old_choice:
            prediction.votes_away_team -= 1
        
        if "home" in new_choice:
            prediction.votes_home_team += 1
        elif "away" in new_choice:
            prediction.votes_away_team += 1
        
        vote.choice = new_choice
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
            prediction.votes_home_team -= 1
        elif "away" in choice:
            prediction.votes_away_team -= 1
        
        prediction.save()
        
        vote.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'status': 'success',
                'message': 'Vote berhasil dihapus!'
            })
        
        messages.success(request, "Vote berhasil dihapus!")
        return redirect('prediction:my_votes')
