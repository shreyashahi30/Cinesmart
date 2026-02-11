fetch("/api/popular")
  .then(res => res.json())
  .then(data => {
    const movies = data.results;
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

      card.onclick = () => openMovie(movie.id);
      container.appendChild(card);
    });
  });

function openMovie(id) {
  fetch(`/api/movie/${id}`)
    .then(res => res.json())
    .then(movie => {
      document.getElementById("modal-body").innerHTML = `
        <h2>${movie.title}</h2>
        <p>${movie.overview}</p>
      `;
      document.getElementById("movie-detail-modal").style.display = "block";
    });
}

document.getElementById("close-modal").onclick = () => {
  document.getElementById("movie-detail-modal").style.display = "none";
};
