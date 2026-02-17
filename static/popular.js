document.addEventListener("DOMContentLoaded", function () {

  const searchInput = document.getElementById("search-bar");
  const container = document.getElementById("movies");

  if (!searchInput || !container) return;

  searchInput.addEventListener("keyup", function () {

    const query = searchInput.value.trim();

    if (query.length < 2) return;

    fetch(`/search?query=${query}`)
      .then(res => res.json())
      .then(data => {

        container.innerHTML = "";

        data.forEach(movie => {

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

          container.appendChild(card);
        });
      });

  });

});
