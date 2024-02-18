from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error, generate_share
import queries

@app.route("/deletetrack", methods=["POST"])
def deletetrack():
    """This route is for deleting tracks. Deleting a track turns it invisible."""
    trackid = request.form.get("trackid")
    genreid = request.form.get("genreid")
    userid = request.form.get("userid")

    # Redirection depends on where the track was deleted from: the genre page or the profile page.
    # TODO: Confirmation for the deletion.
    if genreid:
        queries.delete_track(trackid)
        genreurl = url_for('genre', id=genreid)
        return redirect(genreurl)
    if userid:
        queries.delete_track(trackid)
        profileurl = url_for('profile', id=userid)
        return redirect(profileurl)

    return error.throw(403)

@app.route("/upload")
def upload():
    genres = queries.get_genres()
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

    data = file.read()
    # TODO: Check file?
    sql = "INSERT INTO Tracks (name, user_id, genre_id, date, data, description, private, sharecode) \
        VALUES (:name, :userid, :genreid, NOW(), :data, :description, :private, :sharecode)"
    db.session.execute(text(sql), {"name":name, "userid":userid, "genreid":genreid, "data":data, "description":description, "private":private, "sharecode":sharecode})
    db.session.commit()

    keywords = request.form["keywords"].lower().split()
    queries.add_keywords(keywords)

    track_url = url_for("track", id=queries.max_trackid())
    return "Upload successful, redirecting to track page...", {"Refresh": "3; url="+track_url}

@app.route("/uploadversion/<int:track_id>")
def uploadversion(track_id):
    sql = "SELECT name FROM Tracks WHERE id=:trackid"
    result = db.session.execute(text(sql), {"trackid":track_id})
    track_name = result.fetchone()[0]
    return render_template("upload_version.html", track_id=track_id, track_name=track_name)

@app.route("/sendversion", methods=["POST"])
def sendversion():
    """Uploads a new version of an existing track to showcase alongside previous versions."""
    file = request.files["file"]
    track_id = request.form["track_id"]
    changelog = request.form["changelog"]

    data = file.read()
    # TODO: Check file?
    # The version number is determined by fetching versions with the correct
    # track id and adding one. The original becomes "version 0".
    version_count = db.session.execute(text("SELECT COUNT(id) FROM Versions \
            WHERE track_id=:trackid"), \
            {"trackid":track_id}).fetchone()[0]
    version_number = version_count + 1

    sql = "INSERT INTO Versions (version_number, track_id, data, changelog) \
        VALUES (:version_number, :trackid, :data, :changelog)"
    db.session.execute(text(sql), {"version_number":version_number, "trackid":track_id, "data":data, "changelog":changelog})
    db.session.commit()

    return "OK"

@app.route("/edittrack/<int:id>")
def edittrack(id):
    sql = "SELECT Tracks.id AS trackid, name, genre_id, description, private, Users.id AS userid FROM Tracks LEFT JOIN Users ON Tracks.user_id=Users.id WHERE Tracks.id=:id"
    result = db.session.execute(text(sql), {"id":id})
    trackinfo = result.fetchone()

    keywords = queries.get_keywords(id)
    if keywords:
        keywordstring = ' '.join(word[0] for word in keywords)

    if "userid" not in session:
        error.throw(403)
    elif session["userid"] != trackinfo.userid:
        error.throw(403)

    sql2 = "SELECT id, name FROM Genres"
    result2 = db.session.execute(text(sql2))
    genres = result2.fetchall()

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
    trackid = request.form["trackid"]

    sql = "UPDATE Tracks SET name=:name, genre_id=:genre_id, description=:description, private=:private WHERE id=:trackid"
    db.session.execute(text(sql), {"name":name, "genre_id":genre_id, "description":description, "private":private, "trackid":trackid})
    db.session.commit()

    keywords = request.form["keywords"].lower().split()
    queries.add_keywords(keywords, trackid)

    track_url = url_for('track', id=trackid)
    return redirect(track_url)

# This route plays a track in the database.
@app.route("/play/<int:track_id>/<int:version_id>")
def play(track_id, version_id):
    if version_id == 0:
        sql = "SELECT data FROM Tracks WHERE id=:track_id"
    elif version_id > 0:
        sql = "SELECT data FROM Versions \
            WHERE track_id=:track_id AND version_number=:version_id"
    result = db.session.execute(text(sql), {"track_id":track_id, "version_id":version_id})
    data = result.fetchone()[0]
    response = make_response(bytes(data))
    response.headers.set("Content-Type", "audio/mpeg")
    return response

@app.route("/track/<int:id>")
def track(id):
    # Fetch the file and info:
    track_sql = "SELECT * FROM Tracks WHERE id=:id"
    result = db.session.execute(text(track_sql), {"id":id})
    track = result.fetchone()

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
    version_sql = "SELECT * FROM Versions WHERE track_id=:id"
    result = db.session.execute(text(version_sql), {"id":id})
    versions = result.fetchall()

    # Fetch the comments for the track:
    comment_sql = "SELECT user_id, Comments.id, content, date, username FROM Comments LEFT JOIN Users on Comments.user_id=Users.id WHERE track_id=:id ORDER BY date DESC"
    result = db.session.execute(text(comment_sql), {"id":id})
    comments = result.fetchall()

    return render_template("track.html", track=track, versions=versions, comments=comments, sharelink=sharelink)