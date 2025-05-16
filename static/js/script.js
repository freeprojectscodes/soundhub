document.addEventListener("DOMContentLoaded", function () {
  let currentAudio = new Audio();
  let currentButton = null;

  document.querySelectorAll(".play-btn").forEach(button => {
    button.addEventListener("click", () => {
      const src = button.dataset.src;

      if (currentAudio.src === location.origin + src) {
        if (!currentAudio.paused) {
          currentAudio.pause();
          button.querySelector(".icon").classList.replace("pause-icon", "play-icon");
        } else {
          currentAudio.play();
          button.querySelector(".icon").classList.replace("play-icon", "pause-icon");
        }
      } else {
        document.querySelectorAll(".play-btn .icon").forEach(icon => {
          icon.classList.remove("pause-icon");
          icon.classList.add("play-icon");
        });

        currentAudio.src = src;
        currentAudio.play();

        const icon = button.querySelector(".icon");
        icon.classList.replace("play-icon", "pause-icon");

        currentButton = button;
      }

      currentAudio.onended = () => {
        if (currentButton) {
          const icon = currentButton.querySelector(".icon");
          icon.classList.replace("pause-icon", "play-icon");
        }
      };
    });
  });

  // Star functionality
  document.querySelectorAll(".star-btn").forEach(button => {
    button.addEventListener("click", () => {
      button.classList.toggle("starred");
      button.textContent = button.classList.contains("starred") ? "★" : "☆";
    });
  });

  // Filter search
  const searchInput = document.getElementById("search");
  searchInput.addEventListener("input", () => {
    const filter = searchInput.value.toLowerCase();
    const rows = document.querySelectorAll("#audioTable tbody tr");

    rows.forEach(row => {
      const title = row.querySelector("td[data-label='Track title']")?.innerText.toLowerCase() || '';
      const artist = row.querySelector("td[data-label='Artist']")?.innerText.toLowerCase() || '';
      const genre = row.querySelector("td[data-label='Genre']")?.innerText.toLowerCase() || '';

      const match = title.includes(filter) || artist.includes(filter) || genre.includes(filter);
      row.style.display = match ? "" : "none";
    });
  });
});
