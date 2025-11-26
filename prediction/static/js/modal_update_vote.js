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

  if (currentVote.toLowerCase().includes("home")) {
    currentVoteEl.textContent = homeTeam;
  } else if (currentVote.toLowerCase().includes("away")) {
    currentVoteEl.textContent = awayTeam;
  } else {
    currentVoteEl.textContent = currentVote || "—";
  }


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
  console.log("Update vote response:", data);

  if (data.status === "success") {
    showToast("Success", "Vote berhasil diupdate! 🎉", "success");
    modalUpdateVote.classList.add("hidden");

    // 🔍 cari kartu berdasarkan prediction_id
    const card = document.querySelector(`.prediction-card[data-prediction-id='${data.prediction_id}']`);
    
    if (card) {
    Object.assign(card.dataset, {
        voted: "true",
        userChoice: selectedChoice,
        votedAt: new Date().toLocaleString(),
        voteId: data.vote_id || card.dataset.voteId,
        homeVotes: data.votes_home_team,
        awayVotes: data.votes_away_team,
        homePercentage: data.home_percentage,
        awayPercentage: data.away_percentage,
    });

    // hide elemen lama
    card.querySelectorAll(".voted-badge, .vote-timestamp, .change-vote-trigger, .delete-vote-btn, .vote-trigger")
        .forEach(el => (el.style.display = "none"));

    // 🔄 update hasil vote di UI
    const homePercent = parseFloat(data.home_percentage).toFixed(1);
    const awayPercent = parseFloat(data.away_percentage).toFixed(1);

    const homeRow = card.querySelector(".result-row:nth-child(1)");
    const awayRow = card.querySelector(".result-row:nth-child(2)");

    if (homeRow && awayRow) {
        homeRow.querySelector(".result-percent").textContent = `${homePercent}%`;
        awayRow.querySelector(".result-percent").textContent = `${awayPercent}%`;

        homeRow.querySelector(".result-fill").style.width = `${homePercent}%`;
        awayRow.querySelector(".result-fill").style.width = `${awayPercent}%`;

        homeRow.querySelector(".result-votes").textContent = 
        `${data.votes_home_team} vote${data.votes_home_team == 1 ? '' : 's'}`;
        awayRow.querySelector(".result-votes").textContent = 
        `${data.votes_away_team} vote${data.votes_away_team == 1 ? '' : 's'}`;
    }

    if (typeof window.refreshCardUI === "function") window.refreshCardUI(card);
    if (typeof window.refreshAllCards === "function") window.refreshAllCards();

    console.log("✅ Updated card found:", card);
    }

  } else {
    showToast("Error", data.message || "Gagal update vote.", "error");
  }
})

  .catch(err => {
    console.error("Update vote error:", err);
    showToast("Error", "Terjadi kesalahan saat update vote.", "error");
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
