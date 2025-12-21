from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from scoreboard.models import Match
from .forms import HighlightForm
from .models import Highlight
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def highlight_detail(request, match_id):
    
    match = get_object_or_404(Match, id=match_id)
    highlight = getattr(match, 'highlight', None)

    context = {
        'match': match,
        'highlight': highlight,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'home_score': match.home_score,
        'away_score': match.away_score,
        'home_team_flag': f"https://flagcdn.com/w80/{match.home_team_code.lower()}.png" if match.home_team_code else None,
        'away_team_flag': f"https://flagcdn.com/w80/{match.away_team_code.lower()}.png" if match.away_team_code else None,
    }

    return render(request, 'highlight.html', context)


def highlight_create(request, match_id):
    
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "Anda tidak memiliki izin untuk membuat highlight.")
        return redirect('highlights:match_highlights', match_id=match_id)

    match = get_object_or_404(Match, id=match_id)

    if hasattr(match, "highlight"):
        messages.warning(request, "Highlight untuk pertandingan ini sudah ada.")
        return redirect("highlights:match_highlights", match_id=match.id)

    if request.method == "POST":
        form = HighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.match = match
            highlight.save()
            messages.success(request, "Highlight berhasil ditambahkan!")
            return redirect("highlights:match_highlights", match_id=match.id)
        else:
            messages.error(request, "Terjadi kesalahan. Periksa kembali input Anda.")
    else:
        form = HighlightForm()

    context = {
        "form": form,
        "match": match,
    }
    return render(request, "highlight_form.html", context)


def highlight_update(request, match_id):
    
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "Anda tidak memiliki izin untuk mengedit highlight.")
        return redirect('highlights:match_highlights', match_id=match_id)

    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)

    if request.method == "POST":
        form = HighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            messages.success(request, "Highlight berhasil diperbarui!")
            return redirect('highlights:match_highlights', match_id=match.id)
        else:
            messages.error(request, "Terjadi kesalahan. Periksa input Anda.")
    else:
        form = HighlightForm(instance=highlight)

    context = {
        'form': form,
        'match': match,
        'highlight': highlight,
        'action': 'Update',
    }

    return render(request, 'highlight_form.html', context)


def highlight_delete(request, match_id):
    if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
        messages.error(request, "Anda tidak memiliki izin untuk menghapus highlight.")
        return redirect('highlights:match_highlights', match_id=match_id)

    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)

    highlight.delete()
    messages.success(request, "Highlight berhasil dihapus.")
    return redirect('highlights:match_highlights', match_id=match.id)

def api_highlight_detail(request, match_id):
    # if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
    #     return JsonResponse({"error": "Authentication required"}, status=401)
    match = get_object_or_404(Match, id=match_id)
    highlight = getattr(match, "highlight", None)
    
    return JsonResponse({
        "match": {
            "id": match.id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_team_code": match.home_team_code,
            "away_team_code": match.away_team_code,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "match_date": match.match_date.isoformat(),
            "stadium": match.stadium,
            "round": match.round,
            "group": match.group,
            "status": match.status,
        },
        "highlight": {
            "id": highlight.id if highlight else None,
            "video": highlight.video if highlight else None,
        }
    })

@csrf_exempt
def api_highlight_create(request, match_id):
    # if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
    #     return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    match = get_object_or_404(Match, id=match_id)

    # Prevent duplicate
    if hasattr(match, "highlight"):
        return JsonResponse({"error": "Highlight already exists"}, status=400)

    body = json.loads(request.body.decode("utf-8"))
    video_url = body.get("video", "")

    highlight = Highlight.objects.create(match=match, video=video_url)

    return JsonResponse({
        "id": highlight.id,
        "match_id": match.id,
        "video": highlight.video,
    })

@csrf_exempt
def api_highlight_update(request, match_id):

    # if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
    #     return JsonResponse({"error": "Authentication required"}, status=401)
    if request.method not in ["POST", "PUT"]:
        return JsonResponse({"error": "POST or PUT required"}, status=405)

    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)

    body = json.loads(request.body.decode("utf-8"))
    video_url = body.get("video", "")

    highlight.video = video_url
    highlight.save()

    return JsonResponse({
        "id": highlight.id,
        "match_id": match.id,
        "video": highlight.video,
    })

@csrf_exempt
def api_highlight_delete(request, match_id):
    # if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
    #     return JsonResponse({"error": "Authentication required"}, status=401)
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE required"}, status=405)

    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)

    highlight.delete()

    return JsonResponse({"success": True})



