document.addEventListener("DOMContentLoaded", function () {

  const container = document.getElementById("movies");
  if (!container) return;

  fetch("/api/popular")
    .then(res => res.json())
    .then(data => {

      container.innerHTML = "";

      data.results.forEach(movie => {

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

        card.addEventListener("click", () => openMovie(movie.id));

        container.appendChild(card);
      });
    });

});
