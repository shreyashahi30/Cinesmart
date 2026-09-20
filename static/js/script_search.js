const searchBar = document.getElementById("search-bar");
const movieList = document.getElementById("movies");

let timeout = null;

searchBar.addEventListener("input", function () {

    clearTimeout(timeout);

    timeout = setTimeout(() => {

        const query = searchBar.value.trim();

        if (query.length < 3) {
            movieList.innerHTML = "";
            return;
        }

        fetch(`/search?query=${query}`)
            .then(response => response.json())
            .then(data => {

                movieList.innerHTML = "";

                if (data.length === 0) {
                    movieList.innerHTML = "<p>No movies found</p>";
                    return;
                }

                data.forEach(movie => {

                    const poster = movie.poster_path
                        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                        : "/static/default.jpg";

                    const card = document.createElement("div");
                    card.className = "movie-card";
                    card.innerHTML = `
                        <img src="${poster}" width="120">
                        <h3>${movie.title}</h3>
                        <p>⭐ ${movie.vote_average}</p>
                    `;

                    card.addEventListener("click", () => openMovieModal(movie.id));

                    movieList.appendChild(card);
                });

            })
            .catch(err => console.log("Search error:", err));

    }, 600); // waits 0.6 sec before calling backend

});
