from django.shortcuts import render
from .models import Prediction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Prediction, Vote

# Create your views here.

def prediction_list(request):
    # ambil semua prediction + join ke match biar efisien
    predictions = Prediction.objects.select_related('match').all()


    # bagi jadi 3 kategori berdasarkan status match
    upcoming_predictions = predictions.filter(match__status='upcoming')
    live_predictions = predictions.filter(match__status='live')
    finished_predictions = predictions.filter(match__status='finished')

    context = {
        'upcoming_predictions': upcoming_predictions,
        'live_predictions': live_predictions,
        'finished_predictions': finished_predictions,
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

        # Cek apakah user sudah pernah vote di prediction ini
        if Vote.objects.filter(user=request.user, prediction=prediction).exists():
            return JsonResponse({"status": "error", "message": "You already voted."})

        # Simpan vote user
        Vote.objects.create(user=request.user, prediction=prediction, choice=choice)

        # Update jumlah vote
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