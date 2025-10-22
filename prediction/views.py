from django.shortcuts import render, get_object_or_404
from .models import Prediction

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