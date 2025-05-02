async function fetchMovies() {
    try {
        const response = await fetch('/api/movies');
        const movies = await response.json();
        
        console.log("Movies fetched:", movies); // Log the movies data

        const container = document.getElementById('movie-cards-container');
        container.innerHTML = ''; // Clear any previous content

        movies.forEach(movie => {
            const imageSrc = movie.PosterURL || 'path_to_placeholder_image.jpg';  // Placeholder for missing posters
            const releaseDate = new Date(movie.Released).toLocaleDateString();  // Format release date

            // Dynamically creating the card structure
            const card = `
                <div class="col-md-3 mb-4"> <!-- Bootstrap column for responsiveness -->
                    <div class="card" style="height: 100%; display: flex; flex-direction: column;">
                        ${imageSrc ? ` 
                            <div class="card-img-container" style="position: relative; width: 100%; height: 200px; overflow: hidden; background-color: #DCE4C9;">
                                <img src="${imageSrc}" class="card-img-top" alt="${movie.Title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null; this.src='path_to_placeholder_image.jpg';">
                            </div>
                        ` : ''}

                        <div class="card-body">
                            <div class="card-title-container">
                                <h5 class="card-title" style="word-wrap: break-word; white-space: normal; overflow: hidden; text-overflow: ellipsis;">${movie.Title}</h5>
                            </div>
                            <div class="card-text-container">
                                <p class="card-text"><strong>Release Date:</strong> ${new Date(movie.Released).toLocaleDateString()}</p>
                            </div>
                            <div class="card-button-container mt-auto">
                                <!-- Pass movie ID as a query parameter in the href -->
                                <a href="/moviereview?movie_id=${movie.MovieID}" class="btn btn-primary" style="background: #1E201E; color: white; border: none;">
                                    <button>More Info</button>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += card; // Append each movie card to the container
        });
    } catch (error) {
        console.error("Error fetching movies:", error);
    }
}

fetchMovies();
