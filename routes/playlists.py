from flask import redirect, render_template, request, session, url_for
from app import app
from utils import error
from queries import playlist_queries, track_queries
from utils.check_session import check_csrf

@app.route("/createplaylist", methods=["GET", "POST"])
def createplaylist():
    if session["admin"]:
        tracks = track_queries.get_public_tracks()
    
        if request.method == "POST":
            check_csrf(request)

            track_ids = request.form.getlist('checked')

            if not track_ids:
                return render_template("/createplaylist.html", tracks=tracks, errorm='Error: No tracks selected!')

            if playlist_queries.create_playlist(request):
                return redirect("/adminpanel")
        
        return render_template("createplaylist.html", tracks=tracks,  errorm=request.args.get('errorm'))

    return error.throw(403)

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
    check_csrf(request)

    if playlist_queries.delete_playlist(request):
        return redirect(url_for("manageplaylists"))
    
    return error.throw(400)

@app.route("/editplaylist/<int:id>", methods=["GET", "POST"])
def editplaylist(id):
    if session["admin"]:
        playlist = playlist_queries.get_playlist(id)
        playlisttracks = playlist_queries.get_playlist_tracks(id)
        playlisttrackids = [sub_array[0] for sub_array in playlisttracks]
        alltracks = track_queries.get_public_tracks()

        if request.method == "POST":
            check_csrf(request)

            track_ids = request.form.getlist('checked')

            if not track_ids:
                return render_template("/editplaylist.html", playlist=playlist, playlisttrackids=playlisttrackids, alltracks=alltracks, errorm='Error: No tracks selected!')
    
            if playlist_queries.edit_playlist(request):
                return redirect(url_for("manageplaylists"))

        return render_template("editplaylist.html", playlist=playlist, playlisttrackids=playlisttrackids, alltracks=alltracks, errorm=request.args.get('errorm'))

    return error.throw(403)