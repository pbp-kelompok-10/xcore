// modal_update_vote.js
const modalUpdateVote = document.getElementById("modal-update-vote");
const voteHomeBtn = document.getElementById("vote-home");
const voteAwayBtn = document.getElementById("vote-away");
const confirmSection = document.getElementById("confirm-section");
const voteOptionsSection = document.getElementById("vote-options-section");
const confirmChoice = document.getElementById("confirm-choice");
const confirmUpdateBtn = document.getElementById("confirm-update-btn");
const closeUpdateModalBtn = document.getElementById("close-update-modal");
const currentVoteEl = document.getElementById("current-vote");

let currentVoteId = null;
let selectedChoice = null; // 'home' atau 'away'

// --------------------
// Open Modal
// --------------------
function openUpdateVoteModal(voteId, currentVote, homeTeam, awayTeam) {
  currentVoteId = voteId;
  currentVoteEl.textContent = currentVote;
  document.getElementById("home-team-name").textContent = homeTeam;
  document.getElementById("away-team-name").textContent = awayTeam;

  // Reset state
  selectedChoice = null;
  confirmSection.classList.add("hidden");
  confirmUpdateBtn.classList.add("hidden");
  voteOptionsSection.classList.remove("hidden");
  modalUpdateVote.classList.remove("hidden");
}

// --------------------
// Choose Team
// --------------------
function chooseTeam(choiceKey) {
  selectedChoice = choiceKey; // 'home' atau 'away'
  const teamName = choiceKey === "home"
    ? document.getElementById("home-team-name").textContent
    : document.getElementById("away-team-name").textContent;

  confirmChoice.textContent = teamName;
  voteOptionsSection.classList.add("hidden");
  confirmSection.classList.remove("hidden");
  confirmUpdateBtn.classList.remove("hidden");
}

// --------------------
// Event listeners untuk tombol tim
// --------------------
voteHomeBtn.addEventListener("click", () => chooseTeam("home"));
voteAwayBtn.addEventListener("click", () => chooseTeam("away"));

// --------------------
// Close modal
// --------------------
closeUpdateModalBtn.addEventListener("click", () => {
  modalUpdateVote.classList.add("hidden");
});

// --------------------
// Confirm update vote (AJAX)
// --------------------
confirmUpdateBtn.addEventListener("click", () => {
  if (!selectedChoice) {
    alert("Pilih tim terlebih dahulu!");
    return;
  }
  if (!currentVoteId) {
    alert("Vote ID tidak ditemukan!");
    return;
  }

  fetch("/prediction/update-vote/", {
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
        modalUpdateVote.classList.add("hidden");

        const card = document.querySelector(`.prediction-card[data-vote-id='${data.vote_id}']`);
        if (card) {
          card.dataset.voted = "true";
          card.dataset.userChoice = selectedChoice;
          card.dataset.votedAt = new Date().toLocaleString();
          card.dataset.homeVotes = data.votes_home_team;
          card.dataset.awayVotes = data.votes_away_team;
          card.dataset.homePercentage = data.home_percentage;
          card.dataset.awayPercentage = data.away_percentage;
          if (typeof window.refreshCardUI === "function") window.refreshCardUI(card);
        }

        showToast('Success', 'Vote berhasil diupdate! 🎉', 'success');
      } else {
        alert(data.message || "Gagal update vote.");
      }
    })
    .catch(err => {
      console.error("Update vote error:", err);
      alert("Terjadi kesalahan saat update vote.");
    });
});

// --------------------
// CSRF helper
// --------------------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(c => {
      if (c.trim().startsWith(name + "="))
        cookieValue = decodeURIComponent(c.trim().substring(name.length + 1));
    });
  }
  return cookieValue;
}

// --------------------
// Event untuk tombol Change Vote
// --------------------
document.addEventListener("click", (e) => {
  const target = e.target;
  if (target.matches(".change-vote-trigger") || target.closest(".change-vote-trigger")) {
    const btn = target.closest(".change-vote-trigger");
    const card = btn.closest(".prediction-card");
    if (!card) return;

    const voteId = card.dataset.voteId;
    const currentVote = card.dataset.userChoice || "";
    const homeTeam = card.dataset.homeTeam || "Home";
    const awayTeam = card.dataset.awayTeam || "Away";

    openUpdateVoteModal(voteId, currentVote, homeTeam, awayTeam);
  }
});
