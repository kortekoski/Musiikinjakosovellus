from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries

@app.route("/")
def index():
    """The index of the application. Shows the genre areas where the tracks are plus editor spotlight & playlists."""
    genresql = "SELECT id, name FROM Genres"
    genreresult = db.session.execute(text(genresql))
    genres = genreresult.fetchall()

    spotlightsql = "SELECT Spotlight.track_id, Tracks.name, Users.username FROM Spotlight \
        LEFT JOIN Tracks ON Spotlight.track_id=Tracks.id \
        LEFT JOIN Users ON Users.id=Tracks.user_id \
        WHERE Tracks.visible=True"
    spotlightresult = db.session.execute(text(spotlightsql))
    spotlight = spotlightresult.fetchall()

    info = {}
    for genre in genres:
        genreid = genre.id
        # Get counts of the tracks in each genre (skip invisible and private tracks)
        public_count = db.session.execute(text("SELECT COUNT(name) FROM Tracks \
            WHERE genre_id=:genreid AND visible=True AND private=False"), \
            {"genreid":genreid}).fetchone()[0]
        # Get counts of the private tracks in each genre
        private_count = db.session.execute(text("SELECT COUNT(name) FROM Tracks \
            WHERE genre_id=:genreid AND visible=True AND private=True"), \
            {"genreid":genreid}).fetchone()[0]
        # Get the last uploaded track (skip invisible and private tracks)
        last_uploaded = db.session.execute(text("SELECT date FROM Tracks \
            WHERE genre_id=:genreid AND visible=True AND private=False \
            ORDER BY date DESC"), \
            {"genreid":genreid}).fetchone()
        # Get the last uploaded track from all tracks
        last_uploaded_admin = db.session.execute(text("SELECT date FROM Tracks \
            WHERE genre_id=:genreid AND visible=True \
            ORDER BY date DESC"), \
            {"genreid":genreid}).fetchone()

        infotuple = (public_count, private_count, last_uploaded, last_uploaded_admin)
        info[genreid] = infotuple
    
    playlists = queries.get_playlists()

    return render_template("index.html", genres=genres, spotlight=spotlight, info=info, playlists=playlists)

@app.route("/searchresult")
def searchresult():
    """Searches the database for tracks. The query has to partially match the track name or keywords linked to the track."""
    query = request.args["query"].lower()
    tracks = queries.search(query)
    return render_template("result.html", tracks=tracks)

@app.route("/genre/<int:id>")
def genre(id):
    sql = "SELECT Tracks.id, Tracks.user_id, Tracks.name AS trackname, Tracks.private, Genres.name AS genrename, Genres.id AS genre_id, Users.username from Tracks \
        LEFT JOIN Genres ON Tracks.genre_id=Genres.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE Tracks.genre_id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    genretracks = result.fetchall()
    return render_template("genre.html", genretracks=genretracks)