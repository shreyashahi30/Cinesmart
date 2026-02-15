// script.js

// Replace 'YOUR_TMDB_API_KEY' with your actual TMDB API key
const apiKey = 'd8fb378b6567392adbfae7049c722249';
const popularMoviesUrl = `https://api.themoviedb.org/3/movie/popular?api_key=${apiKey}`;

// Function to fetch and display popular movies
function fetchPopularMovies() {
    fetch(popularMoviesUrl)
        .then(response => response.json())
        .then(data => {
            const movies = data.results;
            const moviesContainer = document.getElementById('movies');
            moviesContainer.innerHTML = ''; // Clear any existing content

            movies.forEach(movie => {
                // Create movie card elements
                const movieCard = document.createElement('div');
                movieCard.classList.add('movie-card');
                movieCard.dataset.movieId = movie.id; // Store movie ID for later use

                const moviePoster = document.createElement('img');
                moviePoster.src = `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
                moviePoster.alt = `${movie.title} Poster`;

                const movieTitle = document.createElement('h3');
                movieTitle.textContent = movie.title;

                const movieRating = document.createElement('p');
                movieRating.textContent = `Rating: ${movie.vote_average}`;

                // Append elements to movie card
                movieCard.appendChild(moviePoster);
                movieCard.appendChild(movieTitle);
                movieCard.appendChild(movieRating);

                // Append movie card to container
                moviesContainer.appendChild(movieCard);

                // Add click event listener to the movie card
                movieCard.addEventListener('click', () => {
                    console.log("Movie clicked:", movie.title)
                    const movieId = movieCard.dataset.movieId;
                    fetchMovieDetails(movieId);
                });
            });
        })
        .catch(error => console.error('Error fetching popular movies:', error));
}

// Function to fetch and display movie details in a modal
function fetchMovieDetails(movieId) {
    const movieDetailsUrl = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}&language=en-US`;

    fetch(movieDetailsUrl)
        .then(response => response.json())
        .then(movie => {
            // Populate modal with movie details
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = ''; // Clear previous content

            // Create elements for movie details
            const backdropPath = movie.backdrop_path || movie.poster_path;
            const movieImage = document.createElement('img');
            movieImage.src = `https://image.tmdb.org/t/p/w780${backdropPath}`;
            movieImage.alt = `${movie.title} Image`;

            const movieTitle = document.createElement('h2');
            movieTitle.textContent = movie.title;

            const movieOverview = document.createElement('p');
            movieOverview.textContent = movie.overview;

            const genresContainer = document.createElement('div');
            genresContainer.classList.add('genres');
            movie.genres.forEach(genre => {
                const genreSpan = document.createElement('span');
                genreSpan.textContent = genre.name;
                genresContainer.appendChild(genreSpan);
            });

            const rating = document.createElement('p');
            rating.classList.add('rating');
            rating.textContent = `Rating: ${movie.vote_average} / 10`;

            const releaseDate = document.createElement('p');
            releaseDate.classList.add('release-date');
            releaseDate.textContent = `Release Date: ${movie.release_date}`;

            // Append elements to modal body
            modalBody.appendChild(movieImage);
            modalBody.appendChild(movieTitle);
            modalBody.appendChild(rating);
            modalBody.appendChild(releaseDate);
            modalBody.appendChild(genresContainer);
            modalBody.appendChild(movieOverview);

            // Show the modal
            const modal = document.getElementById('movie-detail-modal');
            modal.style.display = 'block';
        })
        .catch(error => console.error('Error fetching movie details:', error));
}

// Function to close the modal
function closeModal() {
    const modal = document.getElementById('movie-detail-modal');
    modal.style.display = 'none';
}

const closeBtn = document.getElementById("close-modal");

if (closeBtn) {
    closeBtn.addEventListener("click", closeModal);
}


const modal = document.getElementById("movie-detail-modal");

if (modal) {
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });
}


// Single DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function() {
    fetchPopularMovies();
    // Place other code that needs to run after DOM is loaded here
});
