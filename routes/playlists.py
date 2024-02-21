from flask import redirect, render_template, request, session, url_for
from app import app
from utils import error
from queries import playlist_queries, track_queries

@app.route("/createplaylist")
def createplaylist():
    if session["admin"]:
        tracks = track_queries.get_tracks()
        return render_template("createplaylist.html", tracks=tracks)

    return error.throw(403)

@app.route("/registerplaylist", methods=["POST"])
def registerplaylist():
    if playlist_queries.create_playlist(request):
        return redirect("/adminpanel")

    return error.throw(400)

@app.route("/playlist/<int:id>")
def playlist(id):
    tracks = playlist_queries.get_playlist_tracks(id)

    return render_template("playlist.html", tracks=tracks)

@app.route("/manageplaylists")
def manageplaylists():
    if session["admin"]:
        playlists = playlist_queries.get_playlists()
        return render_template("manageplaylists.html", playlists=playlists)
    
    return error.throw(403)

@app.route("/deleteplaylist", methods=["POST"])
def deleteplaylist():
    if playlist_queries.delete_playlist(request):
        return redirect(url_for("manageplaylists"))
    
    return error.throw(400)

@app.route("/editplaylist/<int:id>")
def editplaylist(id):
    if session["admin"]:
        playlist = playlist_queries.get_playlist(id)
        playlisttracks = playlist_queries.get_playlist_tracks(id)
        playlisttrackids = [sub_array[0] for sub_array in playlisttracks]
        alltracks = track_queries.get_tracks()
        return render_template("editplaylist.html", playlist=playlist, playlisttrackids=playlisttrackids, alltracks=alltracks)

    return error.throw(403)

@app.route("/sendplaylistedit", methods=["POST"])
def sendplaylistedit():
    if playlist_queries.edit_playlist(request):
        return redirect(url_for("manageplaylists"))

    return error.throw(400)