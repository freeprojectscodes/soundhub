document.addEventListener("DOMContentLoaded", function () {
  const waveSurfers = {};
  let currentId = null;

  document.querySelectorAll("tr[data-audio-id]").forEach(row => {
    const id = row.dataset.audioId;
    const src = row.querySelector(".play-btn").dataset.src;
    const container = row.querySelector(`#waveform-${id}`);

    const wavesurfer = WaveSurfer.create({
      container: container,
      waveColor: "#999",
      progressColor: "#3ea6ff",
      height: 48,
      barWidth: 2,
      responsive: true,
      cursorColor: 'transparent',
      showCursor: false,
    });

    wavesurfer.load(src);
    waveSurfers[id] = wavesurfer;

    const playBtn = row.querySelector(".play-btn");

    playBtn.addEventListener("click", () => {
      if (currentId && currentId !== id) {
        waveSurfers[currentId].pause();
        updateButton(currentId, "play");
      }

      if (wavesurfer.isPlaying()) {
        wavesurfer.pause();
        updateButton(id, "play");
        currentId = null;
      } else {
        wavesurfer.play();
        updateButton(id, "pause");
        currentId = id;
      }
    });

    wavesurfer.on("finish", () => {
      updateButton(id, "play");
      if (currentId === id) currentId = null;
    });
  });

  function updateButton(id, state) {
    const icon = document.querySelector(`.play-btn[data-id="${id}"] .icon`);
    icon.classList.remove("play-icon", "pause-icon");
    icon.classList.add(state === "pause" ? "pause-icon" : "play-icon");
  }

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
    document.querySelectorAll("#audioTable tbody tr").forEach(row => {
      const title = row.querySelector("td[data-label='Track title']")?.innerText.toLowerCase() || '';
      const artist = row.querySelector("td[data-label='Artist']")?.innerText.toLowerCase() || '';
      const genre = row.querySelector("td[data-label='Genre']")?.innerText.toLowerCase() || '';
      const match = title.includes(filter) || artist.includes(filter) || genre.includes(filter);
      row.style.display = match ? "" : "none";
    });
  });
});
