from flask import render_template, request
from app import app
from queries import track_queries, playlist_queries, genre_queries

@app.route("/")
def index():
    """The index of the application. Shows the genre areas where the tracks are plus editor spotlight & playlists."""
    genres = genre_queries.get_genres()
    spotlight = track_queries.get_spotlight()
    first_spotlight = spotlight[0]
    rest_spotlight = spotlight[1:]

    info = {}
    for genre in genres:
        genreid = genre.id

        # Get counts of the tracks in each genre (skip invisible and private tracks)
        public_count = genre_queries.public_count(genreid)

        # Get counts of the private tracks in each genre
        private_count = genre_queries.private_count(genreid)

        # Get the last uploaded track (skip invisible and private tracks)
        last_uploaded = genre_queries.last_uploaded(genreid)

        # Get the last uploaded track from all tracks
        last_uploaded_admin = genre_queries.last_uploaded_admin(genreid)

        infotuple = (public_count, private_count, last_uploaded, last_uploaded_admin)
        info[genreid] = infotuple
    
    playlists = playlist_queries.get_playlists()

    return render_template("index.html", genres=genres, first_spotlight=first_spotlight, rest_spotlight=rest_spotlight, info=info, playlists=playlists)

@app.route("/searchresult")
def searchresult():
    """Searches the database for tracks. The query has to partially match the track name or keywords linked to the track."""
    query = request.args["query"].lower()
    tracks = track_queries.search(query)
    return render_template("result.html", tracks=tracks)

@app.route("/genre/<int:id>")
def genre(id):
    genretracks = genre_queries.get_genretracks(id)
    return render_template("genre.html", genretracks=genretracks)