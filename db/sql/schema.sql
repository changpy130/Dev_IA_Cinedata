CREATE TABLE IF NOT EXISTS movies (
    movielens_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS movie_details (
    movielens_id INTEGER PRIMARY KEY,
    release_date DATE,
    budget INTEGER,
    revenue INTEGER,
    runtime INTEGER,
    vote_average FLOAT,
    tagline TEXT,
    plot TEXT,
    FOREIGN KEY (movielens_id) REFERENCES movies(movielens_id)
);

CREATE TABLE IF NOT EXISTS links (
    movielens_id INTEGER PRIMARY KEY,
    tmdb_id INTEGER UNIQUE,
    imdb_id INTEGER UNIQUE,
    FOREIGN KEY (movielens_id) REFERENCES movies(movielens_id)
);

CREATE TABLE IF NOT EXISTS crew (
    tmdb_id INTEGER,
    person_id INTEGER,
    job TEXT,
    PRIMARY KEY (tmdb_id, person_id),
    FOREIGN KEY (tmdb_id) REFERENCES links(tmdb_id),
    FOREIGN KEY (person_id) REFERENCES people(person_id)
);

CREATE TABLE IF NOT EXISTS movie_cast (
    tmdb_id INTEGER,
    person_id INTEGER,
    character TEXT,
    PRIMARY KEY (tmdb_id, person_id),
    FOREIGN KEY (tmdb_id) REFERENCES links(tmdb_id),
    FOREIGN KEY (person_id) REFERENCES people(person_id)
);

CREATE TABLE IF NOT EXISTS people (
    person_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS movie_genres (
    tmdb_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (tmdb_id, genre_id),
    FOREIGN KEY (tmdb_id) REFERENCES links(tmdb_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY,
    genre_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id INTEGER,
    movielens_id INTEGER,
    rating FLOAT,
    PRIMARY KEY (user_id, movielens_id),
    FOREIGN KEY (movielens_id) REFERENCES movies(movielens_id)
);