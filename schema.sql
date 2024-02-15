CREATE TABLE Users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT, 
    admin BOOLEAN DEFAULT FALSE);

CREATE TABLE Genres (
    id SERIAL PRIMARY KEY, 
    name TEXT);

CREATE TABLE Tracks (
    id SERIAL PRIMARY KEY, 
    name TEXT, 
    user_id INTEGER REFERENCES Users ON DELETE CASCADE ON UPDATE CASCADE, 
    genre_id INTEGER REFERENCES Genres ON DELETE CASCADE ON UPDATE CASCADE, 
    date TIMESTAMP, 
    data BYTEA,
    description TEXT,
    visible BOOLEAN DEFAULT TRUE,
    private BOOLEAN);

CREATE TABLE Versions (
    id SERIAL PRIMARY KEY, 
    version_number INTEGER, 
    track_id INTEGER REFERENCES Tracks ON DELETE CASCADE,
    data BYTEA,
    changelog TEXT);

CREATE TABLE Keywords (
    id SERIAL PRIMARY KEY, 
    content TEXT);

CREATE TABLE KeywordsTracks (
    keyword_id INTEGER REFERENCES Keywords ON DELETE CASCADE, 
    track_id INTEGER REFERENCES Tracks ON DELETE CASCADE);

CREATE TABLE Comments (
    id SERIAL PRIMARY KEY, 
    content TEXT, 
    date TIMESTAMP, 
    track_id INTEGER REFERENCES Tracks ON DELETE CASCADE, 
    user_id INTEGER REFERENCES Users);

CREATE TABLE Spotlight (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES Tracks ON DELETE CASCADE);

CREATE TABLE Playlists (
    id SERIAL PRIMARY KEY,
    name TEXT);

CREATE TABLE PlaylistsTracks (
    playlist_id INTEGER REFERENCES Playlists ON DELETE CASCADE,
    track_id INTEGER REFERENCES Tracks ON DELETE CASCADE);
