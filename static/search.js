const input = document.getElementById("searchInput");

let timer = null;

if (input) {
  input.addEventListener("keyup", function () {
    clearTimeout(timer);

    timer = setTimeout(() => {
      const query = input.value.trim();

      if (query.length < 3) return;

      fetch(`/search?query=${query}`)
        .then(res => res.json())
        .then(movies => {
          const container = document.getElementById("movies");
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

  // ✅ Modal opens on click
  card.onclick = () => openMovie(movie.id);

  container.appendChild(card);
});


            container.appendChild(card);
          });
        });

    }, 700);
  });
}
