(function () {
  'use strict';

  function refreshCardUI(card) {
    if (!card) return;
    try {
      // 1. Ambil status terbaru (Pastikan ini dibaca sebagai boolean)
      const voted = String(card.dataset.voted || '').trim().toLowerCase() === 'true';
      const status = (card.dataset.status || '').toLowerCase();
      
      // 2. Select Elements (TARGET LANGSUNG TOMBOLNYA)
      const voteNowBtn = card.querySelector('.vote-trigger');
      const changeBtn = card.querySelector('.change-vote-trigger');
      const deleteBtn = card.querySelector('.delete-vote-btn');
      
      // Elements Badge & Timestamp
      const votedBadge = card.querySelector('.voted-badge');
      const voteTimestamp = card.querySelector('.vote-timestamp');
      const badgeTextEl = card.querySelector('.vote-choice-text'); // Text di dalam badge (opsional)

      // Helper update text
      function updateTextUI() {
          if (votedBadge) {
             let choice = String(card.dataset.userChoice || '').toLowerCase();
             let teamName = card.dataset.userChoice || '-';
             
             if (choice.includes('home')) teamName = card.dataset.homeTeam;
             else if (choice.includes('away')) teamName = card.dataset.awayTeam;
             
             // Update text jika ada elemen khusus, atau langsung innerHTML
             if(badgeTextEl) {
                 badgeTextEl.textContent = teamName;
             } else {
                 // Fallback jika struktur HTML lama
                 votedBadge.innerHTML = `✅ You voted: <strong>${teamName}</strong>`;
             }
          }
          if (voteTimestamp && card.dataset.votedAt) {
             voteTimestamp.textContent = `🕒 Voted at ${card.dataset.votedAt}`;
          }
      }

      // 3. LOGIC UTAMA (BRUTE FORCE VISIBILITY)
      if (status === 'upcoming') {
        if (voted) {
          // --- SUDAH VOTE ---
          // Matikan tombol Vote Now
          if (voteNowBtn) voteNowBtn.style.display = 'none';

          // NYALAKAN tombol Change & Delete & Badge SECARA PAKSA
          if (changeBtn) changeBtn.style.display = 'block';
          if (deleteBtn) deleteBtn.style.display = 'block';
          if (votedBadge) votedBadge.style.display = 'block';
          if (voteTimestamp) voteTimestamp.style.display = 'block';
          
          updateTextUI();

        } else {
          // --- BELUM VOTE ---
          // Nyalakan tombol Vote Now
          if (voteNowBtn) {
              voteNowBtn.style.display = 'block';
              voteNowBtn.disabled = false;
          }

          // Matikan yang lain
          if (changeBtn) changeBtn.style.display = 'none';
          if (deleteBtn) deleteBtn.style.display = 'none';
          if (votedBadge) votedBadge.style.display = 'none';
          if (voteTimestamp) voteTimestamp.style.display = 'none';
        }
      } 
      // Logic FINISHED / LIVE
      else {
        if (voteNowBtn) voteNowBtn.style.display = 'none';
        if (changeBtn) changeBtn.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';

        if (voted) {
            if (votedBadge) votedBadge.style.display = 'block';
            updateTextUI();
        } else {
            if (votedBadge) votedBadge.style.display = 'none';
        }
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

      let visibleCount = 0;

      predictionCards.forEach(card => {
        const isVoted = String(card.dataset.voted || '').toLowerCase() === 'true';
        const status = (card.dataset.status || '').toLowerCase();

        // 1. Tentukan Visibilitas
        let shouldShow = false;
        if (filter === 'all') shouldShow = true;
        else if (filter === 'myvotes') shouldShow = isVoted; // <-- INI YANG BIKIN MUNCUL DI MY VOTES
        else shouldShow = (status === filter);

        // 2. Terapkan Display
        if (shouldShow) {
          card.style.display = ''; // Reset ke default CSS (biasanya block)
          refreshCardUI(card);     // <-- INI AKAN JALAN DAN MEMUNCULKAN TOMBOL
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      // 3. Empty State
      if (emptyState) {
        const emptyMessages = {
          'all': { icon: '📭', title: 'No predictions available', message: 'Check back later!' },
          'myvotes': { icon: '📊', title: "You haven't voted yet", message: 'Start voting in "All Matches"!' },
          'default': { icon: '🔍', title: 'No matches found', message: 'Try a different filter.' }
        };
        const msg = emptyMessages[filter] || emptyMessages['default'];
        
        emptyState.querySelector('.empty-icon').textContent = msg.icon;
        emptyState.querySelector('.empty-title').textContent = msg.title;
        emptyState.querySelector('.empty-message').textContent = msg.message;

        emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
      }
    } catch (err) {
      console.error('refreshAllCards error', err);
    }
  }

  function setupTabHandlers() {
    document.querySelectorAll('.tab-btn[data-filter]').forEach(btn => {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        refreshAllCards();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setupTabHandlers();
    refreshAllCards();
  });

  window.refreshAllCards = refreshAllCards;
  window.refreshCardUI = refreshCardUI;

})();