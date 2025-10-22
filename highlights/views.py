from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from scoreboard.models import Match
from .forms import HighlightForm, HighlightCreateForm
from .models import Highlight


# ============ READ OPERATIONS ============

def highlight_test(request):
    """Test endpoint to display a sample highlights page with a working embed"""
    context = {
        'highlight': {
            'match': {
                'home_team': 'Portugal',
                'away_team': 'Belgium',
                'home_score': 1,
                'away_score': 3,
            },
            'video': 'https://www.youtube.com/embed/tgbNymZ7vqY',
        },
        'home_team_flag': 'https://flagcdn.com/w320/pt.png',
        'away_team_flag': 'https://flagcdn.com/w320/be.png',
    }
    return render(request, 'highlight.html', context)


def highlight_test_create_form(request):
    """Test endpoint to display the create highlight form with a dummy match"""
    # Create or get a dummy match for testing
    dummy_match, created = Match.objects.get_or_create(
        home_team='Test Home Team',
        away_team='Test Away Team',
        defaults={
            'home_score': 2,
            'away_score': 1,
            'match_date': timezone.now() + timedelta(days=1),
            'stadium': 'Test Stadium',
            'status': 'upcoming',
        }
    )
    
    # Check if highlight already exists
    if hasattr(dummy_match, 'highlight'):
        return redirect('highlight_detail', match_id=dummy_match.id)
    
    if request.method == "POST":
        form = HighlightCreateForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.match = dummy_match
            highlight.save()
            return redirect('highlight_detail', match_id=dummy_match.id)
    else:
        form = HighlightCreateForm()
    
    context = {
        'form': form,
        'match': dummy_match,
        'action': 'Create',
        'is_test': True,
    }
    
    return render(request, 'highlight_form.html', context)


def highlight_test_update_form(request):
    """Test endpoint to display the update highlight form with a dummy match and highlight"""
    # Create or get a dummy match for testing
    dummy_match, created = Match.objects.get_or_create(
        home_team='Test Home Team',
        away_team='Test Away Team',
        defaults={
            'home_score': 2,
            'away_score': 1,
            'match_date': timezone.now() + timedelta(days=1),
            'stadium': 'Test Stadium',
            'status': 'upcoming',
        }
    )
    
    # Create a dummy highlight if it doesn't exist
    highlight, created = Highlight.objects.get_or_create(
        match=dummy_match,
        defaults={
            'video': 'https://www.youtube.com/embed/tgbNymZ7vqY',
        }
    )
    
    if request.method == "POST":
        form = HighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            return redirect('highlight_detail', match_id=dummy_match.id)
    else:
        form = HighlightForm(instance=highlight)
    
    context = {
        'form': form,
        'match': dummy_match,
        'highlight': highlight,
        'action': 'Update',
        'is_test': True,
    }
    
    return render(request, 'highlight_form.html', context)


def highlight_detail(request, match_id):
    """
    Read operation: Retrieve and display highlight for a specific match
    """
    match = get_object_or_404(Match, id=match_id)
    highlight = getattr(match, 'highlight', None)
    
    context = {
        'highlight': highlight,
        'home_team_flag': '',  # Add flag URLs from your team data source
        'away_team_flag': '',  # Add flag URLs from your team data source
    }
    
    return render(request, 'highlight.html', context)


# ============ CREATE OPERATIONS ============

@login_required
def highlight_create(request, match_id):
    """
    Create operation: Create a new highlight for a specific match
    Only superusers can create highlights
    """
    # Superuser permission check
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to create highlights.")
    
    match = get_object_or_404(Match, id=match_id)
    
    # Prevent duplicate highlights for the same match
    if hasattr(match, 'highlight'):
        return redirect('highlight_detail', match_id=match.id)
    
    if request.method == "POST":
        form = HighlightCreateForm(request.POST)
        if form.is_valid():
            # Create the highlight for this match
            highlight = form.save(commit=False)
            highlight.match = match
            highlight.save()
            return redirect('highlight_detail', match_id=match.id)
    else:
        form = HighlightCreateForm()
    
    context = {
        'form': form,
        'match': match,
        'action': 'Create',
    }
    
    return render(request, 'highlight_form.html', context)


# ============ UPDATE OPERATIONS ============

@login_required
def highlight_update(request, match_id):
    """
    Update operation: Update an existing highlight
    Only superusers can update highlights
    """
    # Superuser permission check
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to update highlights.")
    
    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)
    
    if request.method == "POST":
        form = HighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            return redirect('highlight_detail', match_id=match.id)
    else:
        form = HighlightForm(instance=highlight)
    
    context = {
        'form': form,
        'match': match,
        'highlight': highlight,
        'action': 'Update',
    }
    
    return render(request, 'highlight_form.html', context)


# ============ DELETE OPERATIONS ============

@login_required
def highlight_delete(request, match_id):
    """
    Delete operation: Delete a highlight
    Only superusers can delete highlights
    """
    # Superuser permission check
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to delete highlights.")
    
    match = get_object_or_404(Match, id=match_id)
    highlight = get_object_or_404(Highlight, match=match)
    
    highlight.delete()
    return redirect('highlight_detail', match_id=match.id)


# ============ LEGACY/DEPRECATED ============

@login_required
def add_highlight(request, match_id=None):
    """
    Legacy function: Use highlight_create instead
    Only superusers allowed
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to add highlights.")

    if match_id:
        match = get_object_or_404(Match, id=match_id)
        if hasattr(match, 'highlight'):
            return redirect('highlight_detail', match_id=match.id)

    if request.method == "POST":
        form = HighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save()
            return redirect('highlight_detail', match_id=highlight.match.id)
    else:
        form = HighlightForm(initial={'match': match_id} if match_id else None)

    return render(request, "highlight_form.html", {"form": form})
