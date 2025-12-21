(function () {
  'use strict';

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  const deleteModalSelector = '#delete-modal';
  let deleteModal = null;

  function openDeleteModalFromCard(card) {
    deleteModal = deleteModal || document.querySelector(deleteModalSelector);
    if (!deleteModal) return;

    // Set Text
    const home = card.dataset.homeTeam || 'Home';
    const away = card.dataset.awayTeam || 'Away';
    const choice = card.dataset.userChoice || '';

    deleteModal.querySelector('#modal-match-home').textContent = home;
    deleteModal.querySelector('#modal-match-away').textContent = away;
    
    let choiceText = choice;
    if(choice.includes('home')) choiceText = home;
    if(choice.includes('away')) choiceText = away;
    deleteModal.querySelector('#modal-vote-choice').textContent = choiceText;

    // Store IDs
    deleteModal.dataset.voteId = card.dataset.voteId;
    deleteModal.dataset.predictionId = card.dataset.predictionId;

    deleteModal.classList.remove('hidden');
  }

  window.closeDeleteModal = function() {
    deleteModal = deleteModal || document.querySelector(deleteModalSelector);
    if(deleteModal) deleteModal.classList.add('hidden');
  };

  window.confirmDelete = function() {
    deleteModal = deleteModal || document.querySelector(deleteModalSelector);
    const voteId = deleteModal.dataset.voteId;
    const predictionId = deleteModal.dataset.predictionId;
    const btn = deleteModal.querySelector('.btn-modal-delete');

    if(btn) btn.disabled = true;

    fetch(`/prediction/my-votes/delete/${encodeURIComponent(voteId)}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            if(typeof showToast === 'function') showToast('Success', 'Vote deleted!', 'success');
            
            // 1. Update Card State
            const card = document.querySelector(`[data-prediction-id="${predictionId}"]`);
            if(card) {
                card.dataset.voted = 'false'; // IMPORTANT
                card.dataset.voteId = '';
                card.dataset.userChoice = '';
                
                // Update stats (decrement)
                card.dataset.homeVotes = data.votes_home_team;
                card.dataset.awayVotes = data.votes_away_team;
                card.dataset.homePercentage = Number(data.home_percentage).toFixed(1);
                card.dataset.awayPercentage = Number(data.away_percentage).toFixed(1);

                // Update Result Bars
                const homeRow = card.querySelector('.results-section .result-row:first-child');
                const awayRow = card.querySelector('.results-section .result-row:last-child');
                
                if(homeRow) {
                   homeRow.querySelector('.result-votes').textContent = `${data.votes_home_team} votes`;
                   homeRow.querySelector('.result-percent').textContent = `${data.home_percentage}%`;
                   homeRow.querySelector('.result-fill').style.width = `${data.home_percentage}%`;
                }
                if(awayRow) {
                   awayRow.querySelector('.result-votes').textContent = `${data.votes_away_team} votes`;
                   awayRow.querySelector('.result-percent').textContent = `${data.away_percentage}%`;
                   awayRow.querySelector('.result-fill').style.width = `${data.away_percentage}%`;
                }

                // 2. REFRESH ALL CARDS (Update My Votes Tab)
                if(typeof window.refreshCardUI === 'function') window.refreshCardUI(card);
                if(typeof window.refreshAllCards === 'function') window.refreshAllCards();
            }
            closeDeleteModal();
        } else {
            if(typeof showToast === 'function') showToast('Error', data.message, 'error');
        }
    })
    .finally(() => {
        if(btn) btn.disabled = false;
    });
  };

  document.addEventListener('click', function(e) {
    if(e.target.matches('.delete-vote-btn') || e.target.closest('.delete-vote-btn')) {
        const btn = e.target.closest('.delete-vote-btn');
        const card = btn.closest('.prediction-card');
        openDeleteModalFromCard(card);
    }
  });

})();