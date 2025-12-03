// modal_delete.js
// Handle delete vote modal and confirm delete flow.
// Provides closeDeleteModal() and confirmDelete() because HTML uses inline onclick.

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
    if (!deleteModal) {
      console.error('Delete modal (#delete-modal) not found.');
      if (typeof showToast === 'function') showToast('Error', 'Delete modal tidak ditemukan!', 'error');
      return;
    }
    // populate texts
    const home = card.dataset.homeTeam || '';
    const away = card.dataset.awayTeam || '';
    const choice = card.dataset.userChoice || '';

    const homeEl = deleteModal.querySelector('#modal-match-home');
    const awayEl = deleteModal.querySelector('#modal-match-away');
    const choiceEl = deleteModal.querySelector('#modal-vote-choice');

    if (homeEl) homeEl.textContent = home;
    if (awayEl) awayEl.textContent = away;
    if (choiceEl) {
      if (String(choice).toLowerCase().includes('home')) choiceEl.textContent = home;
      else if (String(choice).toLowerCase().includes('away')) choiceEl.textContent = away;
      else choiceEl.textContent = choice;
    }

    // store vote id & prediction id on modal for later confirmDelete()
    deleteModal.dataset.voteId = card.dataset.voteId || '';
    deleteModal.dataset.predictionId = card.dataset.predictionId || '';

    deleteModal.classList.remove('hidden');
  }

  // Close functions used by inline onclick in HTML
  window.closeDeleteModal = function closeDeleteModal() {
    deleteModal = deleteModal || document.querySelector(deleteModalSelector);
    if (!deleteModal) return;
    deleteModal.classList.add('hidden');
    delete deleteModal.dataset.voteId;
    delete deleteModal.dataset.predictionId;
  };

  // Confirm delete called by inline onclick in HTML
  window.confirmDelete = function confirmDelete() {
    deleteModal = deleteModal || document.querySelector(deleteModalSelector);
    if (!deleteModal) {
      console.error('confirmDelete called but deleteModal missing');
      if (typeof showToast === 'function') showToast('Error', 'Delete modal tidak tersedia!', 'error');
      return;
    }
    const voteId = deleteModal.dataset.voteId;
    const predictionId = deleteModal.dataset.predictionId;

    if (!voteId) {
      if (typeof showToast === 'function') showToast('Error', 'Vote ID tidak ditemukan!', 'error');
      return;
    }

    const btn = deleteModal.querySelector('.btn-modal-delete');
    if (btn) btn.disabled = true;

    fetch(`/prediction/my-votes/delete/${encodeURIComponent(voteId)}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (data.status === 'success') {
        if (typeof showToast === 'function') showToast('Success', 'Vote berhasil dihapus! 🎉', 'success');

        // update card dataset
        let card = null;
        if (predictionId) card = document.querySelector(`[data-prediction-id="${predictionId}"]`);
        if (!card && voteId) card = document.querySelector(`[data-vote-id="${voteId}"]`);

        if (card) {
          card.dataset.voted = 'false';
          card.dataset.voteId = '';
          card.dataset.userChoice = '';
          card.dataset.votedAt = '';
          card.dataset.homeVotes = String(data.votes_home_team || card.dataset.homeVotes || '0');
          card.dataset.awayVotes = String(data.votes_away_team || card.dataset.awayVotes || '0');
          card.dataset.homePercentage = (typeof data.home_percentage !== 'undefined') ? Number(data.home_percentage).toFixed(1) : (card.dataset.homePercentage || '0');
          card.dataset.awayPercentage = (typeof data.away_percentage !== 'undefined') ? Number(data.away_percentage).toFixed(1) : (card.dataset.awayPercentage || '0');

          // update visible nodes
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

          // refresh UI
          if (typeof window.refreshCardUI === 'function') window.refreshCardUI(card);
        }

        // hide modal and refresh all cards (so My Votes filter updates)
        deleteModal.classList.add('hidden');
        if (typeof window.refreshAllCards === 'function') window.refreshAllCards();
      } else {
        if (typeof showToast === 'function') showToast('Error', data.message || 'Gagal menghapus vote.', 'error');
      }
    })
    .catch(err => {
      console.error('confirmDelete error', err);
      if (typeof showToast === 'function') showToast('Error', `Gagal menghapus vote: ${err.message}`, 'error');
    })
    .finally(() => {
      if (btn) btn.disabled = false;
    });
  };

  // Delegated click to open delete modal when clicking .delete-vote-btn
  document.addEventListener('click', function (e) {
    const target = e.target;
    if (target.matches('.delete-vote-btn') || target.closest('.delete-vote-btn')) {
      const btn = target.matches('.delete-vote-btn') ? target : target.closest('.delete-vote-btn');
      const card = btn.closest('.prediction-card');
      if (!card) {
        console.error('delete-vote-btn clicked but no card found');
        return;
      }
      openDeleteModalFromCard(card);
      return;
    }
  }, false);

})();
