from flask import redirect, render_template, request, session, make_response, url_for
from app import app
from utils import error, generate_share
from queries import track_queries, genre_queries

@app.route("/deletetrack", methods=["POST"])
def deletetrack():
    """This route is for deleting tracks. Deleting a track turns it invisible."""
    trackid = request.form.get("trackid")
    genreid = request.form.get("genreid")
    userid = request.form.get("userid")

    # Redirection depends on where the track was deleted from: the genre page or the profile page.
    # TODO: Confirmation for the deletion.
    if genreid:
        track_queries.delete_track(trackid)
        genreurl = url_for('genre', id=genreid)
        return redirect(genreurl)
    if userid:
        track_queries.delete_track(trackid)
        profileurl = url_for('profile', id=userid)
        return redirect(profileurl)

    return error.throw(403)

@app.route("/upload")
def upload():
    genres = genre_queries.get_genres()
    return render_template("upload.html", genres=genres)

@app.route("/send", methods=["POST"])
def send():
    file = request.files["file"]
    userid = session["userid"]
    name = request.form["trackname"]
    description = request.form["description"]
    genreid = request.form["genre"]
    private = request.form["private"]
    sharecode = generate_share.generate_sharecode()

    # TODO: Check if required fields are filled (name?) and that there is a file.
    # TODO: Check file?
    data = file.read()

    track_queries.add_track(name, userid, genreid, data, description, private, sharecode)

    keywords = request.form["keywords"].lower().split()
    track_queries.add_keywords(keywords)

    track_url = url_for("track", id=track_queries.max_trackid())
    return "Upload successful, redirecting to track page...", {"Refresh": "3; url="+track_url}

@app.route("/uploadversion/<int:track_id>")
def uploadversion(track_id):
    track = track_queries.get_track(track_id)
    track_name = track[1]
    return render_template("upload_version.html", track_id=track_id, track_name=track_name)

@app.route("/sendversion", methods=["POST"])
def sendversion():
    """Uploads a new version of an existing track to showcase alongside previous versions."""
    file = request.files["file"]
    track_id = request.form["track_id"]
    changelog = request.form["changelog"]

    data = file.read()
    # TODO: Check file?
    
    track_queries.add_version(track_id, data, changelog)

    track_url = url_for("track", id=track_id)
    return "Upload successful, redirecting to track page...", {"Refresh": "3; url="+track_url}

@app.route("/edittrack/<int:id>")
def edittrack(id):
    trackinfo = track_queries.get_trackinfo(id)

    keywords = track_queries.get_keywords(id)
    if keywords:
        keywordstring = ' '.join(word[0] for word in keywords)

    if "userid" not in session:
        error.throw(403)
    elif session["userid"] != trackinfo.userid:
        error.throw(403)

    genres = genre_queries.get_genres()

    if keywords:
        return render_template("edittrack.html", trackinfo=trackinfo, genres=genres, keywordstring=keywordstring)
    else:
        return render_template("edittrack.html", trackinfo=trackinfo, genres=genres)

@app.route("/sendtrackedit", methods=["POST"])
def sendtrackedit():
    name = request.form["trackname"]
    genre_id = request.form["genre"]
    description = request.form["description"]
    private = request.form["private"]
    track_id = request.form["trackid"]

    track_queries.edit_track(name, genre_id, description, private, track_id)

    keywords = request.form["keywords"].lower().split()
    track_queries.add_keywords(keywords, track_id)

    track_url = url_for('track', id=track_id)
    return redirect(track_url)

# This route plays a track in the database.
@app.route("/play/<int:track_id>/<int:version_id>")
def play(track_id, version_id):
    data = track_queries.get_data(track_id, version_id)
    response = make_response(bytes(data))
    response.headers.set("Content-Type", "audio/mpeg")
    return response

@app.route("/track/<int:id>")
def track(id):
    # Fetch the file and info:
    track = track_queries.get_track(id)

    if not track.visible:
        return error.throw(404)
    
    if track.private:
        sharelink = "Share your track: " + request.url + "?share=" + track.sharecode
    else:
        sharelink = "Share your track: " + request.url
    
    # TODO: Make this code more compact.
    if "userid" in session:
        if track.private and session["userid"] != track.user_id:
            sharecode_in_url = request.args.get("share")

            if not sharecode_in_url or not track.sharecode:
                return error.throw(403)
            
            if track.sharecode != sharecode_in_url:
                return error.throw(403)
    else:
        if track.private:
            sharecode_in_url = request.args.get("share")

            if not sharecode_in_url or not track.sharecode:
                return error.throw(403)
            
            if track.sharecode != sharecode_in_url:
                return error.throw(403)


    # Fetch the versions
    versions = track_queries.get_versions(id)

    # Fetch the comments for the track:
    comments = track_queries.get_track_comments(id)

    return render_template("track.html", track=track, versions=versions, comments=comments, sharelink=sharelink)