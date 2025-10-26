// modal_poll.js
// Handle polling modal (open, close, submit vote to /prediction/submit-vote/)

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

  const modalSelector = '#polling-popup';
  let modal = null;

  function openPollingModalFromCard(card) {
    modal = modal || document.querySelector(modalSelector);
    if (!modal) {
      console.error('Polling modal not found in DOM');
      if (typeof showToast === 'function') showToast('Error', 'Polling modal tidak ditemukan!', 'error');
      return;
    }

    // store prediction id
    modal.dataset.predictionId = card.dataset.predictionId || '';
    // populate team names if spans exist
    const homeSpan = modal.querySelector('.team-home span');
    const awaySpan = modal.querySelector('.team-away span');
    if (homeSpan) homeSpan.textContent = card.dataset.homeTeam || (card.querySelector('.team-name') ? card.querySelector('.team-name').textContent : 'Home');
    if (awaySpan) awaySpan.textContent = card.dataset.awayTeam || 'Away';

    modal.classList.remove('hidden');
  }

  function closePollingModal() {
    modal = modal || document.querySelector(modalSelector);
    if (!modal) return;
    modal.classList.add('hidden');
    // clear prediction id
    delete modal.dataset.predictionId;
  }

  function submitVote(choice, teamBtnEl) {
    modal = modal || document.querySelector(modalSelector);
    if (!modal) {
      console.error('Modal missing when submitting vote');
      if (typeof showToast === 'function') showToast('Error', 'Polling modal tidak tersedia saat submit!', 'error');
      return;
    }
    const predictionId = modal.dataset.predictionId;
    if (!predictionId) {
      if (typeof showToast === 'function') showToast('Error', 'Prediction ID tidak ditemukan!', 'error');
      return;
    }

    // disable clicked button
    if (teamBtnEl) teamBtnEl.disabled = true;

    fetch('/prediction/submit-vote/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: `prediction_id=${encodeURIComponent(predictionId)}&choice=${encodeURIComponent(choice)}`
    })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (data.status === 'success') {
        if (typeof showToast === 'function') showToast('Success', 'Vote berhasil! 🎉', 'success');
        closePollingModal();

        // update the card dataset and UI
        const card = document.querySelector(`[data-prediction-id="${predictionId}"]`);
        if (card) {
          card.dataset.voted = 'true';
          card.dataset.voteId = data.vote_id || '';
          card.dataset.userChoice = choice;
          card.dataset.votedAt = data.voted_at || new Date().toISOString();
          card.dataset.homeVotes = String(data.votes_home_team || card.dataset.homeVotes || '0');
          card.dataset.awayVotes = String(data.votes_away_team || card.dataset.awayVotes || '0');
          card.dataset.homePercentage = (typeof data.home_percentage !== 'undefined') ? Number(data.home_percentage).toFixed(1) : (card.dataset.homePercentage || '0');
          card.dataset.awayPercentage = (typeof data.away_percentage !== 'undefined') ? Number(data.away_percentage).toFixed(1) : (card.dataset.awayPercentage || '0');

          // Update visible result text nodes if present
          const homeVoteElement = card.querySelector('.results-section .result-row:first-child .result-votes');
          const awayVoteElement = card.querySelector('.results-section .result-row:last-child .result-votes');
          const homePercentElement = card.querySelector('.results-section .result-row:first-child .result-percent');
          const awayPercentElement = card.querySelector('.results-section .result-row:last-child .result-percent');
          const homeFillElement = card.querySelector('.results-section .result-row:first-child .result-fill');
          const awayFillElement = card.querySelector('.results-section .result-row:last-child .result-fill');

          if (homeVoteElement) homeVoteElement.textContent = `${card.dataset.homeVotes} vote${card.dataset.homeVotes !== '1' ? 's' : ''}`;
          if (awayVoteElement) awayVoteElement.textContent = `${card.dataset.awayVotes} vote${card.dataset.awayVotes !== '1' ? 's' : ''}`;
          if (homePercentElement) homePercentElement.textContent = `${card.dataset.homePercentage}%`;
          if (awayPercentElement) awayPercentElement.textContent = `${card.dataset.awayPercentage}%`;
          if (homeFillElement) homeFillElement.style.width = `${card.dataset.homePercentage}%`;
          if (awayFillElement) awayFillElement.style.width = `${card.dataset.awayPercentage}%`;

          // Try to refresh card UI & possibly all cards (if available)
          if (typeof window.refreshCardUI === 'function') window.refreshCardUI(card);
          if (typeof window.refreshAllCards === 'function') window.refreshAllCards();
        } else {
          // if card not found, simply refresh all
          if (typeof window.refreshAllCards === 'function') window.refreshAllCards();
        }
      } else {
        if (typeof showToast === 'function') showToast('Error', data.message || 'Gagal menyimpan vote.', 'error');
      }
    })
    .catch(err => {
      console.error('submitVote error', err);
      if (typeof showToast === 'function') showToast('Error', `Gagal menyimpan vote: ${err.message}`, 'error');
    })
    .finally(() => {
      if (teamBtnEl) teamBtnEl.disabled = false;
    });
  }

  // Delegated click handlers
  document.addEventListener('click', function (e) {
    const target = e.target;

    // open modal: click on .vote-trigger (button inside card)
    if (target.matches('.vote-trigger') || target.closest('.vote-trigger')) {
      const btn = target.matches('.vote-trigger') ? target : target.closest('.vote-trigger');
      // if user not logged in, some templates redirect; we assume server handles that
      const card = btn.closest('.prediction-card');
      if (!card) {
        console.error('vote-trigger clicked but no card found');
        return;
      }
      // if already voted, prevent opening (UX)
      if (String(card.dataset.voted || '').toLowerCase() === 'true') {
        if (typeof showToast === 'function') showToast('Warning', 'Kamu sudah vote! Gunakan "Change Vote".', 'warning');
        return;
      }
      openPollingModalFromCard(card);
      return;
    }

    // close modal via close button (SVG button has class popup-close-btn)
    if (target.matches('.popup-close-btn') || target.closest('.popup-close-btn')) {
      closePollingModal();
      return;
    }

    // team button clicked inside modal -> submit
    if (target.matches('.team-btn') || target.closest('.team-btn')) {
      const btn = target.matches('.team-btn') ? target : target.closest('.team-btn');
      const choice = btn.dataset.team; // expected 'home' or 'away'
      if (!choice) {
        if (typeof showToast === 'function') showToast('Error', 'Pilihan tim tidak valid!', 'error');
        return;
      }
      // guard: ensure modal open
      modal = modal || document.querySelector(modalSelector);
      if (!modal || modal.classList.contains('hidden')) {
        if (typeof showToast === 'function') showToast('Error', 'Modal tidak terbuka!', 'error');
        return;
      }
      submitVote(choice, btn);
      return;
    }
  }, false);

  // expose close for safety
  window.closePollingModal = closePollingModal;
})();
