CREATE TABLE Users (
    id SERIAL PRIMARY KEY, 
    username TEXT, 
    password TEXT, 
    admin BOOLEAN DEFAULT FALSE);

CREATE TABLE Genres (
    id SERIAL PRIMARY KEY, 
    name TEXT);

CREATE TABLE Tracks (
    id SERIAL PRIMARY KEY, 
    name TEXT, 
    user_id INTEGER REFERENCES Users, 
    genre_id INTEGER REFERENCES Genres, 
    date TIMESTAMP, 
    data BYTEA);

CREATE TABLE Versions (
    id SERIAL PRIMARY KEY, 
    version_number INTEGER, 
    track_id INTEGER REFERENCES Tracks);

CREATE TABLE Keywords (
    id SERIAL PRIMARY KEY, 
    content TEXT);

CREATE TABLE KeywordsTracks (
    keyword_id INTEGER REFERENCES Keywords, 
    track_id INTEGER REFERENCES Tracks);

CREATE TABLE Comments (
    id SERIAL PRIMARY KEY, 
    content TEXT, date TIMESTAMP, 
    track_id INTEGER REFERENCES Tracks, 
    user_id INTEGER REFERENCES Users);