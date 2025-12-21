// modal_update_vote.js
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

  const modalUpdateVote = document.getElementById("modal-update-vote");
  const voteHomeBtn = document.getElementById("vote-home");
  const voteAwayBtn = document.getElementById("vote-away");
  const confirmSection = document.getElementById("confirm-section");
  const voteOptionsSection = document.getElementById("vote-options-section");
  const confirmChoiceEl = document.getElementById("confirm-choice");
  const confirmUpdateBtn = document.getElementById("confirm-update-btn");
  const closeUpdateModalBtn = document.getElementById("close-update-modal");
  const currentVoteEl = document.getElementById("current-vote");

  let currentVoteId = null;
  let currentPredictionId = null;
  let selectedChoice = null; // 'home' atau 'away'

  // --------------------
  // Open Modal
  // --------------------
  function openUpdateVoteModalFromCard(card) {
    if (!modalUpdateVote) return;

    // Ambil data dari card
    const voteId = card.dataset.voteId;
    const predictionId = card.dataset.predictionId;
    const currentVote = card.dataset.userChoice || '';
    const homeTeam = card.dataset.homeTeam || 'Home';
    const awayTeam = card.dataset.awayTeam || 'Away';

    currentVoteId = voteId;
    currentPredictionId = predictionId;

    // Set Text Tim
    document.getElementById("home-team-name").textContent = homeTeam;
    document.getElementById("away-team-name").textContent = awayTeam;

    // Tampilkan Pilihan Saat Ini
    let displayVote = currentVote;
    if (currentVote.toLowerCase().includes("home")) displayVote = homeTeam;
    else if (currentVote.toLowerCase().includes("away")) displayVote = awayTeam;
    currentVoteEl.textContent = displayVote;

    // Reset State UI Modal
    selectedChoice = null;
    confirmSection.classList.add("hidden");
    confirmUpdateBtn.classList.add("hidden");
    voteOptionsSection.classList.remove("hidden");
    
    modalUpdateVote.classList.remove("hidden");
  }

  function closeUpdateModal() {
    if (modalUpdateVote) modalUpdateVote.classList.add("hidden");
  }

  // --------------------
  // Choose Team Logic
  // --------------------
  function chooseTeam(choiceKey) {
    selectedChoice = choiceKey; // 'home' atau 'away'
    const teamName = choiceKey === "home"
      ? document.getElementById("home-team-name").textContent
      : document.getElementById("away-team-name").textContent;

    confirmChoiceEl.textContent = teamName;
    voteOptionsSection.classList.add("hidden");
    confirmSection.classList.remove("hidden");
    confirmUpdateBtn.classList.remove("hidden");
  }

  // --------------------
  // Event Listeners (Modal Internal)
  // --------------------
  if (voteHomeBtn) voteHomeBtn.addEventListener("click", () => chooseTeam("home"));
  if (voteAwayBtn) voteAwayBtn.addEventListener("click", () => chooseTeam("away"));
  if (closeUpdateModalBtn) closeUpdateModalBtn.addEventListener("click", closeUpdateModal);

  // --------------------
  // Confirm Update (AJAX)
  // --------------------
  if (confirmUpdateBtn) {
    confirmUpdateBtn.addEventListener("click", () => {
      if (!selectedChoice || !currentVoteId) return;

      // Disable tombol saat loading
      confirmUpdateBtn.disabled = true;
      const originalText = confirmUpdateBtn.textContent;
      confirmUpdateBtn.textContent = "Updating...";

      fetch("/prediction/update-vote/", { // Pastikan URL ini benar
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest"
        },
        body: `vote_id=${encodeURIComponent(currentVoteId)}&choice=${encodeURIComponent(selectedChoice)}`
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          if (typeof showToast === 'function') showToast("Success", "Vote updated! 🎉", "success");
          closeUpdateModal();

          // 1. Cari Card yang bersangkutan
          // Gunakan prediction_id dari response atau variabel lokal
          const targetId = data.prediction_id || currentPredictionId;
          const card = document.querySelector(`.prediction-card[data-prediction-id='${targetId}']`);
          
          if (card) {
            // 2. Update Dataset Card (PENTING untuk UI & Tab Filter)
            card.dataset.voted = "true";
            card.dataset.userChoice = selectedChoice;
            card.dataset.voteId = data.vote_id || currentVoteId;
            card.dataset.votedAt = "Just now"; // Atau data.voted_at jika ada dari backend
            
            // Update Statistik
            card.dataset.homeVotes = data.votes_home_team;
            card.dataset.awayVotes = data.votes_away_team;
            card.dataset.homePercentage = Number(data.home_percentage).toFixed(1);
            card.dataset.awayPercentage = Number(data.away_percentage).toFixed(1);

            // 3. Update Visual Bar (Opsional, refreshCardUI biasanya handle tombol aja)
            // Kita update manual bar-nya biar instan
            const homeRow = card.querySelector('.results-section .result-row:first-child');
            const awayRow = card.querySelector('.results-section .result-row:last-child');
            
            if(homeRow) {
               homeRow.querySelector('.result-votes').textContent = `${data.votes_home_team} votes`;
               homeRow.querySelector('.result-percent').textContent = `${Number(data.home_percentage).toFixed(1)}%`;
               homeRow.querySelector('.result-fill').style.width = `${data.home_percentage}%`;
            }
            if(awayRow) {
               awayRow.querySelector('.result-votes').textContent = `${data.votes_away_team} votes`;
               awayRow.querySelector('.result-percent').textContent = `${Number(data.away_percentage).toFixed(1)}%`;
               awayRow.querySelector('.result-fill').style.width = `${data.away_percentage}%`;
            }

            // 4. Trigger Refresh Global (Agar tombol Change/Delete muncul kembali & Filter updated)
            if (typeof window.refreshCardUI === "function") window.refreshCardUI(card);
            if (typeof window.refreshAllCards === "function") window.refreshAllCards();
          }

        } else {
          if (typeof showToast === 'function') showToast("Error", data.message || "Gagal update vote.", "error");
        }
      })
      .catch(err => {
        console.error("Update vote error:", err);
        if (typeof showToast === 'function') showToast("Error", "Terjadi kesalahan koneksi.", "error");
      })
      .finally(() => {
        confirmUpdateBtn.disabled = false;
        confirmUpdateBtn.textContent = originalText;
      });
    });
  }

  // --------------------
  // Global Click Listener (Event Delegation)
  // --------------------
  // Ini menangkap klik tombol "Change Vote" bahkan untuk elemen yang baru dibuat via JS
  document.addEventListener("click", (e) => {
    const target = e.target;
    if (target.matches(".change-vote-trigger") || target.closest(".change-vote-trigger")) {
      const btn = target.closest(".change-vote-trigger");
      const card = btn.closest(".prediction-card");
      if (card) {
        openUpdateVoteModalFromCard(card);
      }
    }
    
    // Tutup jika klik overlay
    if (target === modalUpdateVote) {
        closeUpdateModal();
    }
  });

})();