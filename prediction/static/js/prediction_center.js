// prediction_center.js
(function () {
  'use strict';

  function debug(...args) {
    if (window && window.DEBUG_PREDICTIONS) console.log('[prediction_center]', ...args);
  }

  function refreshCardUI(card) {
  if (!card) return;
  try {
    const voted = String(card.dataset.voted || '').trim().toLowerCase() === 'true';
    const status = (card.dataset.status || '').toLowerCase();

    const activeTab = document.querySelector('.tab-btn.active');
    const isMyVotesTab = activeTab && activeTab.dataset.filter === 'myvotes';

    // Elements inside card
    const votedBadge = card.querySelector('.voted-badge');
    const voteTimestamp = card.querySelector('.vote-timestamp');
    const changeVoteBtn = card.querySelector('.change-vote-trigger');
    const deleteVoteBtn = card.querySelector('.delete-vote-btn');
    const voteNowBtn = card.querySelector('.vote-trigger');
    const votingClosedMsg = card.querySelector('.voting-closed');

    // Reset semua elemen dulu
    [votedBadge, voteTimestamp, changeVoteBtn, deleteVoteBtn, voteNowBtn, votingClosedMsg].forEach(el => {
      if (el) {
        el.style.display = 'none';
        if (el.tagName === 'BUTTON' || el.tagName === 'A') el.disabled = true;
      }
    });

    // Helper buat nulis tim mana yang dipilih
    function setVotedBadgeText() {
      if (!votedBadge) return;
      const strongEl = votedBadge.querySelector('strong');
      const choice = String(card.dataset.userChoice || '').toLowerCase();
      if (strongEl) {
        if (choice.includes('home')) strongEl.textContent = card.dataset.homeTeam || 'Home';
        else if (choice.includes('away')) strongEl.textContent = card.dataset.awayTeam || 'Away';
        else strongEl.textContent = card.dataset.userChoice || 'Unknown';
      }
    }

    // Cek waktu kick-off
    const matchStart = new Date(card.dataset.matchStart || '');
    const now = new Date();
    const diffHours = (matchStart - now) / 3600_000; // jam sampai mulai

    // ========== UPCOMING ==========
    if (status === 'upcoming') {
    if (voted) {
        if (isMyVotesTab) {
        // ✅ hanya tampil di tab My Votes
        if (votedBadge) { votedBadge.style.display = 'block'; setVotedBadgeText(); }
        if (voteTimestamp && card.dataset.votedAt) {
            voteTimestamp.style.display = 'block';
            voteTimestamp.textContent = `🕒 Voted at ${card.dataset.votedAt}`;
        }

        // 🧩 tambahin ini biar tombolnya muncul lagi
        if (changeVoteBtn) { changeVoteBtn.style.display = 'block'; changeVoteBtn.disabled = false; }
        if (deleteVoteBtn) { deleteVoteBtn.style.display = 'block'; deleteVoteBtn.disabled = false; }

        } else {
        // 🔒 di tab lain, sembunyikan badge, tapi kalau klik Vote Now kasih info toast
        if (voteNowBtn) {
            voteNowBtn.style.display = 'block';
            voteNowBtn.disabled = false;
            voteNowBtn.onclick = () => showToast('Info', 'Kamu sudah vote untuk match ini!', 'info');
        }
        }
    } else if (voteNowBtn) {
        // user belum vote → boleh vote di semua tab selain finished
        voteNowBtn.style.display = 'block';
        voteNowBtn.disabled = false;
        voteNowBtn.onclick = null;
    }
    return;
    }



    // ========== LIVE ==========
    if (status === 'live') {
    // Anggap sama kayak finished
    if (voted) {
        if (votedBadge) { votedBadge.style.display = 'block'; setVotedBadgeText(); }
        if (voteTimestamp && card.dataset.votedAt) {
        voteTimestamp.style.display = 'block';
        voteTimestamp.textContent = `🕒 Voted at ${card.dataset.votedAt}`;
        }
    } else if (voteTimestamp) {
        voteTimestamp.style.display = 'block';
        voteTimestamp.textContent = 'You haven’t voted for this match.';
    }
    return;
    }


    // ========== FINISHED ==========
    if (status === 'finished' || diffHours <= 2) { // tambahan: kalau udah lewat 2 jam juga treat as finished
      if (voted) {
        if (votedBadge) { votedBadge.style.display = 'block'; setVotedBadgeText(); }
        if (voteTimestamp && card.dataset.votedAt) {
          voteTimestamp.style.display = 'block';
          voteTimestamp.textContent = `🕒 Voted at ${card.dataset.votedAt}`;
        }
      } else if (voteTimestamp) {
        voteTimestamp.style.display = 'block';
        voteTimestamp.textContent = 'You didn’t vote for this match.';
      }
      return;
    }

  } catch (err) {
    console.error('refreshCardUI error', err);
  }
}


  function refreshAllCards() {
    try {
      const activeTab = document.querySelector('.tab-btn.active');
      const filter = activeTab ? (activeTab.dataset.filter || 'all') : 'all';
      const predictionCards = Array.from(document.querySelectorAll('.prediction-card'));
      const emptyState = document.querySelector('.empty-state-dynamic');

      predictionCards.forEach(card => {
        card.dataset.voted = String(card.dataset.voted || '').toLowerCase() === 'true' ? 'true' : 'false';
        card.dataset.userChoice = card.dataset.userChoice || '';
        card.dataset.votedAt = card.dataset.votedAt || '';
        card.dataset.homeVotes = card.dataset.homeVotes || '0';
        card.dataset.awayVotes = card.dataset.awayVotes || '0';
        card.dataset.homePercentage = card.dataset.homePercentage || '0';
        card.dataset.awayPercentage = card.dataset.awayPercentage || '0';
      });

      let visibleCount = 0;

      function showCard(card) { card.style.display=''; refreshCardUI(card); visibleCount++; }
      function hideCard(card) { card.style.display='none'; }

      predictionCards.forEach(card => {
        if (filter === 'all') showCard(card);
        else if (filter === 'myvotes') (card.dataset.voted==='true') ? showCard(card):hideCard(card);
        else ((card.dataset.status||'').toLowerCase()===filter) ? showCard(card):hideCard(card);
      });

      if (emptyState) {
        const emptyMessages = {
          'all': { icon: '📭', title: 'No predictions available yet', message: 'Check back later for upcoming matches!' },
          'upcoming': { icon: '⏰', title: 'No upcoming matches', message: 'All matches have started or finished!' },
          'live': { icon: '🔴', title: 'No live matches right now', message: 'Check back when matches are in progress!' },
          'finished': { icon: '✅', title: 'No finished matches yet', message: 'Come back after matches are completed!' },
          'myvotes': { icon: '📊', title: "You haven't voted yet", message: 'Start voting for your favorite teams!' }
        };
        const msg = emptyMessages[filter] || emptyMessages['all'];
        const iconNode = emptyState.querySelector('.empty-icon');
        const titleNode = emptyState.querySelector('.empty-title');
        const msgNode = emptyState.querySelector('.empty-message');
        if (iconNode) iconNode.textContent = msg.icon;
        if (titleNode) titleNode.textContent = msg.title;
        if (msgNode) msgNode.textContent = msg.message;

        emptyState.style.display = visibleCount===0 ? 'flex' : 'none';
      }
    } catch (err) {
      console.error('refreshAllCards error', err);
    }
  }

  function setupTabHandlers() {
    document.querySelectorAll('.tab-btn[data-filter]').forEach(btn => {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
        this.classList.add('active');
        refreshAllCards();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setupTabHandlers();
    if (!document.querySelector('.tab-btn.active')) {
      const first = document.querySelector('.tab-btn[data-filter]');
      if (first) first.classList.add('active');
    }
    refreshAllCards();
  });

  window.refreshAllCards = refreshAllCards;
  window.refreshCardUI = refreshCardUI;

})();
