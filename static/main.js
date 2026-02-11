function openMovie(id) {
  fetch(`/api/movie/${id}`)
    .then(res => res.json())
    .then(movie => {

      console.log(movie.poster_path); // ✅ Debug line

      const poster = movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : "/static/default.jpg";

      document.getElementById("modal-body").innerHTML = `
        <img src="${poster}" 
             style="width:200px; border-radius:10px;">
        <h2>${movie.title}</h2>
        <p>${movie.overview}</p>
      `;

      document.getElementById("movie-detail-modal").style.display = "block";
    });
}
