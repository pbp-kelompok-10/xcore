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
    if (!modal) return;

    modal.dataset.predictionId = card.dataset.predictionId || '';
    
    // Set team names in modal
    const homeName = card.dataset.homeTeam || 'Home';
    const awayName = card.dataset.awayTeam || 'Away';

    const homeSpan = modal.querySelector('.team-home span');
    const awaySpan = modal.querySelector('.team-away span');
    if (homeSpan) homeSpan.textContent = homeName;
    if (awaySpan) awaySpan.textContent = awayName;

    modal.classList.remove('hidden');
  }

  function closePollingModal() {
    modal = modal || document.querySelector(modalSelector);
    if (!modal) return;
    modal.classList.add('hidden');
    delete modal.dataset.predictionId;
  }

  function submitVote(choice, teamBtnEl) {
    modal = modal || document.querySelector(modalSelector);
    const predictionId = modal.dataset.predictionId;

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
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        if (typeof showToast === 'function') showToast('Success', 'Vote submitted! 🎉', 'success');
        closePollingModal();

        // 1. Update Card Dataset
        const card = document.querySelector(`[data-prediction-id="${predictionId}"]`);
        if (card) {
          card.dataset.voted = 'true';
          card.dataset.voteId = data.vote_id;
          card.dataset.userChoice = choice;

          // --- PERBAIKAN FORMAT TANGGAL (FIX TIMESTAMP) ---
          const now = new Date();
          
          // Format Angka: 01, 02, ... 21
          const day = String(now.getDate()).padStart(2, '0');
          const hour = String(now.getHours()).padStart(2, '0');
          const minute = String(now.getMinutes()).padStart(2, '0');
          const year = now.getFullYear();

          // Format Bulan: Jan, Feb, ... Dec
          const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
          const month = monthNames[now.getMonth()];

          // GABUNGKAN: "21 Dec 2025, 14:30"
          // Ini biar sama persis kayak format Django
          const formattedDate = `${day} ${month} ${year}, ${hour}:${minute}`;

          // Masukkan tanggal cantik ini ke dataset card
          card.dataset.votedAt = formattedDate;
          // ------------------------------------------------

          
          // Update Stats
          card.dataset.homeVotes = data.votes_home_team;
          card.dataset.awayVotes = data.votes_away_team;
          card.dataset.homePercentage = Number(data.home_percentage).toFixed(1);
          card.dataset.awayPercentage = Number(data.away_percentage).toFixed(1);

          // Update Visual Bar
          const homeRow = card.querySelector('.results-section .result-row:first-child');
          const awayRow = card.querySelector('.results-section .result-row:last-child');
          
          if(homeRow) {
             homeRow.querySelector('.result-votes').textContent = `${data.votes_home_team} vote${data.votes_home_team !== 1 ? 's' : ''}`;
             homeRow.querySelector('.result-percent').textContent = `${Number(data.home_percentage).toFixed(1)}%`;
             homeRow.querySelector('.result-fill').style.width = `${data.home_percentage}%`;
          }
          if(awayRow) {
             awayRow.querySelector('.result-votes').textContent = `${data.votes_away_team} vote${data.votes_away_team !== 1 ? 's' : ''}`;
             awayRow.querySelector('.result-percent').textContent = `${Number(data.away_percentage).toFixed(1)}%`;
             awayRow.querySelector('.result-fill').style.width = `${data.away_percentage}%`;
          }

          // 2. TRIGGER REFRESH UI
          // Fungsi ini akan baca card.dataset.votedAt yang barusan kita rapihin
          if (typeof window.refreshCardUI === 'function') window.refreshCardUI(card);
          if (typeof window.refreshAllCards === 'function') window.refreshAllCards();
        }
      } else {
        if (typeof showToast === 'function') showToast('Error', data.message, 'error');
      }
    });
  }

  // Event Delegation
  document.addEventListener('click', function (e) {
    const target = e.target;

    // Open Modal
    if (target.matches('.vote-trigger') || target.closest('.vote-trigger')) {
      const btn = target.closest('.vote-trigger');
      const card = btn.closest('.prediction-card');
      openPollingModalFromCard(card);
    }

    // Close Modal
    if (target.matches('.popup-close-btn') || target.closest('.popup-close-btn')) {
      closePollingModal();
    }

    // Submit Vote (Home/Away)
    if (target.matches('.team-btn') || target.closest('.team-btn')) {
      const btn = target.closest('.team-btn');
      submitVote(btn.dataset.team, btn);
    }
  });

})();