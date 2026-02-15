// script_popular.js

// Replace with your actual TMDB API key
const apiKey = 'd8fb378b6567392adbfae7049c722249';

const popularMoviesUrl =
  `https://api.themoviedb.org/3/movie/popular?api_key=${apiKey}`;


// Function to fetch and display popular movies
function fetchPopularMovies() {
    fetch(popularMoviesUrl)
        .then(response => response.json())
        .then(data => {

            const movies = data.results;
            const moviesContainer = document.getElementById('movies');
            moviesContainer.innerHTML = '';

            movies.forEach(movie => {

                // Create movie card
                const movieCard = document.createElement('div');
                movieCard.classList.add('movie-card');
                movieCard.dataset.movieId = movie.id;

                const moviePoster = document.createElement('img');
                moviePoster.src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
                moviePoster.alt = `${movie.title} Poster`;

                const movieTitle = document.createElement('h3');
                movieTitle.textContent = movie.title;

                const movieRating = document.createElement('p');
                movieRating.textContent = `Rating: ${movie.vote_average}`;

                movieCard.appendChild(moviePoster);
                movieCard.appendChild(movieTitle);
                movieCard.appendChild(movieRating);

                moviesContainer.appendChild(movieCard);

                // Click event for modal
                movieCard.addEventListener('click', () => {
                    console.log("Movie clicked:", movie.title);
                    fetchMovieDetails(movie.id);
                });
            });
        })
        .catch(error => console.error("Error fetching popular movies:", error));
}


// Function to fetch and show movie details in modal
function fetchMovieDetails(movieId) {

    const movieDetailsUrl =
      `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}&language=en-US`;

    fetch(movieDetailsUrl)
        .then(response => response.json())
        .then(movie => {

            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = '';

            const backdropPath = movie.backdrop_path || movie.poster_path;

            const movieImage = document.createElement('img');
            movieImage.src = `https://image.tmdb.org/t/p/w780${backdropPath}`;
            movieImage.alt = movie.title;

            const movieTitle = document.createElement('h2');
            movieTitle.textContent = movie.title;

            const rating = document.createElement('p');
            rating.textContent = `Rating: ${movie.vote_average} / 10`;

            const releaseDate = document.createElement('p');
            releaseDate.textContent = `Release Date: ${movie.release_date}`;

            const genresContainer = document.createElement('div');
            genresContainer.classList.add("genres");

            movie.genres.forEach(genre => {
                const span = document.createElement("span");
                span.textContent = genre.name;
                genresContainer.appendChild(span);
            });

            const overview = document.createElement('p');
            overview.textContent = movie.overview;

            modalBody.appendChild(movieImage);
            modalBody.appendChild(movieTitle);
            modalBody.appendChild(rating);
            modalBody.appendChild(releaseDate);
            modalBody.appendChild(genresContainer);
            modalBody.appendChild(overview);

            document.getElementById("movie-detail-modal").style.display = "block";
        })
        .catch(error => console.error("Error fetching movie details:", error));
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


// Load popular movies on page load
document.addEventListener("DOMContentLoaded", function () {
    fetchPopularMovies();
});
