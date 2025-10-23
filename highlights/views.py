from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from scoreboard.models import Match
from .forms import HighlightForm
from .models import Highlight

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
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to update highlights.")
    
    match = get_object_or_404(Match, id=match_id)

    # Prevent duplicate highlight per match (since OneToOneField)
    if hasattr(match, "highlight"):
        return redirect("highlights:match_highlights", match_id=match.id)

    if request.method == "POST":
        form = HighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.match = match  # ✅ automatically attach the match
            highlight.save()
            return redirect("highlights:match_highlights", match_id=match.id)
    else:
        form = HighlightForm()

    context = {
        "form": form,
        "match": match,
    }
    return render(request, "highlight_form.html", context)


def highlight_update(request, match_id):

    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to update highlights.")
    
    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)
    
    if request.method == "POST":
        form = HighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            return redirect('highlights:match_highlights', match_id=match.id)
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

    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to delete highlights.")
    
    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)
    
    highlight.delete()
    return redirect('highlights:match_highlights', match_id=match.id)

