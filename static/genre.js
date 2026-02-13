document.addEventListener("DOMContentLoaded", function () {

  const container = document.getElementById("movies");

  // ✅ Safety check
  if (!container) {
    console.error("Movies container not found!");
    return;
  }

  // ✅ Fetch genre movies
  fetch(`/api/genre/${GENRE_ID}`)
    .then(res => res.json())
    .then(data => {

      const movies = data.results;
      container.innerHTML = "";

      movies.forEach(movie => {
        const card = document.createElement("div");
        card.className = "movie-card";

        const poster = movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
          : "/static/default.jpg";

        card.innerHTML = `
          <img src="${poster}">
          <h3>${movie.title}</h3>
          <p>⭐ ${movie.vote_average}</p>
        `;

        // ✅ Modal open on click
        card.onclick = () => openMovie(movie.id);

        container.appendChild(card);
      });
    });

});


// ✅ Movie Detail Modal Function
function openMovie(id) {
  fetch(`/api/movie/${id}`)
    .then(res => res.json())
    .then(movie => {

      const poster = movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : "/static/default.jpg";

      document.getElementById("modal-body").innerHTML = `
        <h2>${movie.title}</h2>
        <img src="${poster}" style="width:200px; border-radius:10px; margin:15px 0;">
        <p>${movie.overview}</p>
      `;

      document.getElementById("movie-detail-modal").style.display = "block";
    });
}


// ✅ Close Modal Button
document.addEventListener("DOMContentLoaded", function () {
  const closeBtn = document.getElementById("close-modal");

  if (closeBtn) {
    closeBtn.onclick = () => {
      document.getElementById("movie-detail-modal").style.display = "none";
    };
  }
});
