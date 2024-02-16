from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries

@app.route("/createplaylist")
def createplaylist():
    if session["admin"]:
        tracks = queries.get_tracks()
        return render_template("createplaylist.html", tracks=tracks)

    return error.throw(403)

@app.route("/registerplaylist", methods=["POST"])
def registerplaylist():
    if queries.create_playlist(request):
        return redirect("/adminpanel")

    return error.throw(400)

@app.route("/playlist/<int:id>")
def playlist(id):
    tracks = queries.get_playlist_tracks(id)

    return render_template("playlist.html", tracks=tracks)

@app.route("/manageplaylists")
def manageplaylists():
    if session["admin"]:
        playlists = queries.get_playlists()
        return render_template("manageplaylists.html", playlists=playlists)
    
    return error.throw(403)

@app.route("/deleteplaylist", methods=["POST"])
def deleteplaylist():
    if queries.delete_playlist(request):
        return redirect(url_for("manageplaylists"))
    
    return error.throw(400)

@app.route("/editplaylist/<int:id>")
def editplaylist(id):
    if session["admin"]:
        playlist = queries.get_playlist(id)
        playlisttracks = queries.get_playlist_tracks(id)
        playlisttrackids = [sub_array[0] for sub_array in playlisttracks]
        alltracks = queries.get_tracks()
        return render_template("editplaylist.html", playlist=playlist, playlisttrackids=playlisttrackids, alltracks=alltracks)

    return error.throw(403)

@app.route("/sendplaylistedit", methods=["POST"])
def sendplaylistedit():
    if queries.edit_playlist(request):
        return redirect(url_for("manageplaylists"))

    return error.throw(400)