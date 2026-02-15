// script_upcoming.js

// Replace with your TMDB API key
const apiKey = 'd8fb378b6567392adbfae7049c722249';

const upcomingMoviesUrl =
  `https://api.themoviedb.org/3/movie/upcoming?api_key=${apiKey}`;



// Function to fetch and display upcoming movies
function fetchUpcomingMovies() {
    fetch(upcomingMoviesUrl)
        .then(response => response.json())
        .then(data => {

            const movies = data.results;
            const moviesContainer = document.getElementById("movies");
            moviesContainer.innerHTML = "";

            movies.forEach(movie => {

                const movieCard = document.createElement("div");
                movieCard.classList.add("movie-card");
                movieCard.dataset.movieId = movie.id;

                const moviePoster = document.createElement("img");
                moviePoster.src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
                moviePoster.alt = movie.title;

                const movieTitle = document.createElement("h3");
                movieTitle.textContent = movie.title;

                const releaseDate = document.createElement("p");
                releaseDate.textContent = `Release Date: ${movie.release_date}`;

                movieCard.appendChild(moviePoster);
                movieCard.appendChild(movieTitle);
                movieCard.appendChild(releaseDate);

                moviesContainer.appendChild(movieCard);

                // Modal click
                movieCard.addEventListener("click", () => {
                    console.log("Upcoming movie clicked:", movie.title);
                    fetchMovieDetails(movie.id);
                });
            });
        })
        .catch(error => console.error("Error fetching upcoming movies:", error));
}



// Function to fetch movie details in modal
function fetchMovieDetails(movieId) {

    const movieDetailsUrl =
      `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}&language=en-US`;

    fetch(movieDetailsUrl)
        .then(response => response.json())
        .then(movie => {

            const modalBody = document.getElementById("modal-body");
            modalBody.innerHTML = "";

            const backdropPath = movie.backdrop_path || movie.poster_path;

            const movieImage = document.createElement("img");
            movieImage.src = `https://image.tmdb.org/t/p/w780${backdropPath}`;
            movieImage.alt = movie.title;

            const movieTitle = document.createElement("h2");
            movieTitle.textContent = movie.title;

            const rating = document.createElement("p");
            rating.textContent = `Rating: ${movie.vote_average} / 10`;

            const releaseDate = document.createElement("p");
            releaseDate.textContent = `Release Date: ${movie.release_date}`;

            const overview = document.createElement("p");
            overview.textContent = movie.overview;

            modalBody.appendChild(movieImage);
            modalBody.appendChild(movieTitle);
            modalBody.appendChild(rating);
            modalBody.appendChild(releaseDate);
            modalBody.appendChild(overview);

            document.getElementById("movie-detail-modal").style.display = "block";
        })
        .catch(error => console.error("Error fetching upcoming movie details:", error));
}



// Close modal
function closeModal() {
    document.getElementById("movie-detail-modal").style.display = "none";
}

document.getElementById("close-modal").addEventListener("click", closeModal);

window.addEventListener("click", function (event) {
    const modal = document.getElementById("movie-detail-modal");
    if (event.target === modal) {
        closeModal();
    }
});


// Load upcoming movies when page opens
document.addEventListener("DOMContentLoaded", function () {
    fetchUpcomingMovies();
});
