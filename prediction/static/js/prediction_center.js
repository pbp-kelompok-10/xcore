(function () {
  'use strict';

  function refreshCardUI(card) {
    if (!card) return;
    try {
      // 1. Ambil Data
      const voted = String(card.dataset.voted || '').trim().toLowerCase() === 'true';
      const status = (card.dataset.status || '').toLowerCase();
      
      const homeTeam = card.dataset.homeTeam || 'Home';
      const awayTeam = card.dataset.awayTeam || 'Away';
      const userChoice = String(card.dataset.userChoice || '').toLowerCase();

      // --- CEK TAB AKTIF ---
      const activeTab = document.querySelector('.tab-btn.active');
      const currentFilter = activeTab ? (activeTab.dataset.filter || 'all') : 'all';

      // --- SELECT ELEMENTS ---
      const voteNowBtn = card.querySelector('.vote-trigger');
      const actionsContainer = card.querySelector('.vote-actions-container'); 
      const votedBadge = card.querySelector('.voted-badge');
      const voteTimestamp = card.querySelector('.vote-timestamp');

      let displayTeamName = userChoice;
      if (userChoice === 'home') displayTeamName = homeTeam;
      if (userChoice === 'away') displayTeamName = awayTeam;

      // Helper Format Tanggal
      function formatNiceDate(dateString) {
          if (!dateString) return '';
          if (dateString.length < 25 && !dateString.includes('/')) return dateString;
          try {
              const date = new Date(dateString);
              if (isNaN(date.getTime())) return dateString;
              const day = String(date.getDate()).padStart(2, '0');
              const year = date.getFullYear();
              const hour = String(date.getHours()).padStart(2, '0');
              const minute = String(date.getMinutes()).padStart(2, '0');
              const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
              const month = monthNames[date.getMonth()];
              return `${day} ${month} ${year}, ${hour}:${minute}`;
          } catch (e) {
              return dateString;
          }
      }

      // --- RESET TAMPILAN (Sembunyikan Semua Dulu) ---
      if (voteNowBtn) voteNowBtn.style.display = 'none';
      if (actionsContainer) actionsContainer.style.display = 'none';
      if (votedBadge) votedBadge.style.display = 'none';
      if (voteTimestamp) voteTimestamp.style.display = 'none';

      // --- LOGIC UTAMA ---
      if (status === 'upcoming') {
          
          if (currentFilter === 'myvotes') {
              // ==============================
              // TAB: MY VOTES
              // ==============================
              if (voted) {
                  // Tampilkan UI "Sudah Vote" Lengkap
                  if (actionsContainer) actionsContainer.style.display = 'flex'; // Tombol Change/Delete
                  
                  if (votedBadge) {
                      votedBadge.style.display = 'block';
                      votedBadge.innerHTML = `✅ You voted: <strong>${displayTeamName}</strong>`;
                  }
                  
                  if (voteTimestamp) {
                      voteTimestamp.style.display = 'block';
                      if (card.dataset.votedAt) {
                          voteTimestamp.textContent = `🕒 Voted at ${formatNiceDate(card.dataset.votedAt)}`;
                      }
                  }
              } 
              // (Jaga-jaga kalau ada kartu belum vote nyasar ke tab My Votes, biarkan kosong/hidden)
          } 
          else {
              // ==============================
              // TAB: ALL MATCHES (Default)
              // ==============================
              // POKOKNYA TAMPILAN SEPERTI BELUM VOTE (Clean)
              
              // 1. Selalu Tampilkan Tombol Vote Now
              if (voteNowBtn) {
                  voteNowBtn.style.display = 'block';
                  voteNowBtn.disabled = false;
              }

              // 2. JANGAN Tampilkan Badge/Timestamp/ChangeButton
              // (Karena di atas sudah kita hide semua di bagian Reset Tampilan, jadi aman)
          }

      } else {
          // --- LIVE / FINISHED ---
          // Tidak ada tombol aksi
          if (voted) {
              // Cuma Badge & Timestamp (Kalau mau ditampilkan di history)
              if (votedBadge) {
                  votedBadge.style.display = 'block';
                  votedBadge.innerHTML = `✅ You voted: <strong>${displayTeamName}</strong>`;
              }
              if (voteTimestamp) voteTimestamp.style.display = 'block';
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

        // 1. Filter Logic
        let shouldShow = false;
        if (filter === 'all') shouldShow = true;
        else if (filter === 'myvotes') shouldShow = isVoted;
        else shouldShow = (status === filter);

        // 2. Display & Refresh UI
        if (shouldShow) {
          card.style.display = ''; 
          refreshCardUI(card); // UI menyesuaikan tab (All vs My Votes)
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      // 3. Empty State Logic
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