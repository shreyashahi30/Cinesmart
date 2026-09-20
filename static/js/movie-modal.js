function openMovieModal(movieId) {
  const modal = document.getElementById("movie-detail-modal");
  const modalBody = document.getElementById("modal-body");

  if (!modal || !modalBody) {
    console.error("Movie modal markup not found on this page.");
    return;
  }

  // Show the modal immediately with a loading state so a slow or failed
  // TMDB request doesn't look like a dead click.
  modalBody.innerHTML = "<p>Loading…</p>";
  modal.style.display = "block";

  fetch(`/api/movie/${movieId}`)
    .then(res => {
      if (!res.ok) {
        // app.py returns 502 + {"error": "..."} when TMDB fails.
        throw new Error(`Request failed (${res.status})`);
      }
      return res.json();
    })
    .then(movie => {
      modalBody.innerHTML = "";

      const backdropPath = movie.backdrop_path || movie.poster_path;
      if (backdropPath) {
        const img = document.createElement("img");
        img.src = `https://image.tmdb.org/t/p/w780${backdropPath}`;
        img.alt = movie.title || "Movie poster";
        modalBody.appendChild(img);
      }

      const title = document.createElement("h2");
      title.textContent = movie.title || "Unknown title";
      modalBody.appendChild(title);

      const rating = document.createElement("p");
      rating.textContent = `⭐ ${movie.vote_average !== undefined ? movie.vote_average : "N/A"} / 10`;
      modalBody.appendChild(rating);

      const release = document.createElement("p");
      release.textContent = `Release Date: ${movie.release_date || "N/A"}`;
      modalBody.appendChild(release);

      if (Array.isArray(movie.genres) && movie.genres.length) {
        const genresContainer = document.createElement("div");
        genresContainer.classList.add("genres");

        movie.genres.forEach(genre => {
          const span = document.createElement("span");
          span.textContent = genre.name;
          span.style.marginRight = "8px";
          genresContainer.appendChild(span);
        });

        modalBody.appendChild(genresContainer);
      }

      const overview = document.createElement("p");
      overview.textContent = movie.overview || "No overview available.";
      modalBody.appendChild(overview);

    })
    .catch(err => {
      console.error("Error fetching movie details:", err);
      modalBody.innerHTML = "<p>Sorry, couldn't load details for this movie right now.</p>";
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("movie-detail-modal");
  const closeBtn = document.getElementById("close-modal");

  if (!modal) return;

  function closeMovieModal() {
    modal.style.display = "none";
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", closeMovieModal);
  }

  window.addEventListener("click", function (event) {
    if (event.target === modal) closeMovieModal();
  });
});
