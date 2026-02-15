// script.js

// Replace 'YOUR_TMDB_API_KEY' with your actual TMDB API key
const apiKey = 'd8fb378b6567392adbfae7049c722249';
const popularMoviesUrl = `https://api.themoviedb.org/3/movie/popular?api_key=${apiKey}`;

// Function to fetch and display popular thriller movies
function fetchPopularMovies() {
    fetch(popularMoviesUrl)
        .then(response => response.json())
        .then(data => {
            const movies = data.results;
            const thrillerMoviesContainer = document.getElementById('movies');
            thrillerMoviesContainer.innerHTML = ''; // Clear any existing content

            // Filter movies by "Thriller" genre (ID: 53)
            const thrillerGenreId = 53; // Thriller genre ID from TMDB
            const thrillerMovies = movies.filter(movie => 
                movie.genre_ids.includes(thrillerGenreId)
            );

            thrillerMovies.forEach(movie => {
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

                const genresContainer = document.createElement('div');
                genresContainer.classList.add('genres');
                const genreNames = movie.genre_ids.map(genreId => getGenreName(genreId)).join(', ');
                genresContainer.textContent = genreNames; // Add all genre names with commas

                // Append elements to movie card
                movieCard.appendChild(moviePoster);
                movieCard.appendChild(movieTitle);
                movieCard.appendChild(movieRating);
                movieCard.appendChild(genresContainer);

                // Append movie card to container
                thrillerMoviesContainer.appendChild(movieCard);

                // Add click event listener to the movie card
                movieCard.addEventListener('click', () => {
                    console.log("Movie clicked:", movie.title);
                    const movieId = movieCard.dataset.movieId;
                    fetchMovieDetails(movieId);
                });
            });
        })
        .catch(error => console.error('Error fetching popular movies:', error));
}

// Function to get genre name by ID
function getGenreName(genreId) {
    const genreMapping = {
        28: 'Action',
        12: 'Adventure',
        16: 'Animation',
        35: 'Comedy',
        80: 'Crime',
        99: 'Documentary',
        18: 'Drama',
        14: 'Fantasy',
        27: 'Horror',
        10402: 'Music',
        9648: 'Mystery',
        10749: 'Romance',
        878: 'Science Fiction',
        10770: 'TV Movie',
        53: 'Thriller',
        10752: 'War',
        37: 'Western',
    };
    return genreMapping[genreId] || ''; // Return an empty string instead of 'Unknown Genre'
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
            const genreNames = movie.genres.map(genre => genre.name).join(', ');
            genresContainer.textContent = genreNames; // Add all genre names with commas

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

// Event listener for closing the modal
document.getElementById('close-modal').addEventListener('click', closeModal);

// Close modal when clicking outside of modal content
window.addEventListener('click', function(event) {
    const modal = document.getElementById('movie-detail-modal');
    if (event.target === modal) {
        closeModal();
    }
});

// Single DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function() {
    fetchPopularMovies();
});
