from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error

@app.route("/")
def index():
    """The index of the application. Shows the genre areas where the tracks are."""
    sql = "SELECT id, name FROM Genres"
    result = db.session.execute(text(sql))
    genres = result.fetchall()

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

    return render_template("index.html", genres=genres, info=info)

# This route is for the search function.
@app.route("/searchresult")
def searchresult():
    query = request.args["query"].lower()
    sql = "SELECT Tracks.id, name, username FROM Tracks \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE LOWER(name) LIKE :query"
    result = db.session.execute(text(sql), {"query":"%"+query+"%"})
    tracks = result.fetchall()
    return render_template("result.html", tracks=tracks)

@app.route("/genre/<int:id>")
def genre(id):
    sql = "SELECT Tracks.id, Tracks.user_id, Tracks.name AS trackname, Tracks.private, Genres.name AS genrename, Genres.id AS genre_id, Users.username from Tracks \
        LEFT JOIN Genres ON Tracks.genre_id=Genres.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id\
        WHERE Tracks.genre_id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    genretracks = result.fetchall()
    return render_template("genre.html", genretracks=genretracks)

@app.route("/profile/<int:id>")
def profile(id):
    sql = "SELECT Users.id AS userid, Users.username, Tracks.id AS trackid, \
        Tracks.name, Tracks.private \
        FROM Users LEFT JOIN Tracks ON Users.id=Tracks.user_id \
        WHERE Users.id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    tracks = result.fetchall()
    return render_template("profile.html", id=id, tracks=tracks)

@app.route("/deletetrack", methods=["POST"])
def deletetrack():
    """This route is for deleting tracks. Deleting a track turns it invisible."""
    trackid = request.form.get("trackid")
    genreid = request.form.get("genreid")
    userid = request.form.get("userid")

    # Redirection depends on where the track was deleted from: the genre page or the profile page.
    # TODO: Confirmation for the deletion.
    if genreid:
        sql = "UPDATE Tracks SET visible=False WHERE id=:trackid"
        db.session.execute(text(sql), {"trackid":trackid})
        db.session.commit()
        genreurl = url_for('genre', id=genreid)
        return redirect(genreurl)
    if userid:
        sql = "UPDATE Tracks SET visible=False WHERE id=:trackid"
        db.session.execute(text(sql), {"trackid":trackid})
        db.session.commit()
        profileurl = url_for('profile', id=userid)
        return redirect(profileurl)

    return error.throw(403)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT id, password, admin FROM Users WHERE username=:username"
        result = db.session.execute(text(sql), {"username":username})
        user = result.fetchone()

        if not user:
            return redirect(url_for('login', error='Invalid username'))
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                # TO CONSIDER: Is this enough feedback for the user?
                session["username"] = username
                session["userid"] = user.id
                session["admin"] = user.admin
                return redirect('/')
            else:
                error = 'Invalid password!'
                return redirect(url_for('login', error='Invalid password'))

    return render_template("login.html", error=request.args.get('error'))

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/registeruser", methods=['POST'])
def registeruser():
    username = request.form["username"]
    password = request.form["password"]
    admin = request.form["admin"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO Users (username, password, admin) VALUES (:username, :password, :admin)"
    db.session.execute(text(sql), {"username":username, "password":hash_value, "admin":admin})
    db.session.commit()
    return "User added to database"

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    session["admin"] = False
    return redirect("/")

@app.route("/upload")
def upload():
    sql = "SELECT * FROM Genres"
    result = db.session.execute(text(sql))
    genres = result.fetchall()
    return render_template("upload.html", genres=genres)

@app.route("/send", methods=['POST'])
def send():
    file = request.files["file"]
    userid = session["userid"]
    name = request.form["trackname"]
    description = request.form["description"]
    genreid = request.form["genre"]
    private = request.form["private"]

    # TODO: The keywords exist but do nothing for now. Seems like adding the functionality would be quite a hassle.
    keywords = request.form["keywords"].lower().split()

    # TODO: Check if required fields are filled (name?) and that there is a file.

    data = file.read()
    # TODO: Check file?
    sql = "INSERT INTO Tracks (name, user_id, genre_id, date, data, description, private) \
        VALUES (:name, :userid, :genreid, NOW(), :data, :description, :private)"
    db.session.execute(text(sql), {"name":name, "userid":userid, "genreid":genreid, "data":data, "description":description, "private":private})
    db.session.commit()


    # TODO: Return "upload successful" or whatever and redirect to the created track page. Could also redirect to the "my tracks" page, which doesn't exist yet.
    genre_url = url_for('genre', id=genreid)
    return redirect(genre_url)

@app.route("/uploadversion/<int:track_id>")
def uploadversion(track_id):
    sql = "SELECT name FROM Tracks WHERE id=:trackid"
    result = db.session.execute(text(sql), {"trackid":track_id})
    track_name = result.fetchone()[0]
    return render_template("upload_version.html", track_id=track_id, track_name=track_name)

@app.route("/sendversion", methods=['POST'])
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

    if "userid" not in session:
        error.throw(403)
    elif session["userid"] != trackinfo.userid:
        error.throw(403)

    sql2 = "SELECT id, name FROM Genres"
    result2 = db.session.execute(text(sql2))
    genres = result2.fetchall()

    return render_template("edittrack.html", trackinfo=trackinfo, genres=genres)

@app.route("/sendtrackedit", methods=['POST'])
def sendtrackedit():
    name = request.form["trackname"]
    genre_id = request.form["genre"]
    description = request.form["description"]
    private = request.form["private"]
    trackid = request.form["trackid"]

    sql = "UPDATE Tracks SET name=:name, genre_id=:genre_id, description=:description, private=:private WHERE id=:trackid"
    db.session.execute(text(sql), {"name":name, "genre_id":genre_id, "description":description, "private":private, "trackid":trackid})
    db.session.commit()

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

    # Fetch the versions
    version_sql = "SELECT * FROM Versions WHERE track_id=:id"
    result = db.session.execute(text(version_sql), {"id":id})
    versions = result.fetchall()

    # Fetch the comments for the track:
    comment_sql = "SELECT user_id, Comments.id, content, date, username FROM Comments LEFT JOIN Users on Comments.user_id=Users.id WHERE track_id=:id"
    result = db.session.execute(text(comment_sql), {"id":id})
    comments = result.fetchall()

    return render_template("track.html", track=track, versions=versions, comments=comments)

@app.route("/comment/<int:track_id>", methods=['POST'])
def comment(track_id):
    comment_text = request.form["newcomment"]
    userid = session["userid"]
    sql = "INSERT INTO Comments (content, date, track_id, user_id) \
        VALUES (:content, NOW(), :id, :userid)"
    db.session.execute(text(sql), {"content":comment_text, "id":track_id, "userid":userid})
    db.session.commit()
    track_url = url_for('track', id=track_id)

    return redirect(track_url)

@app.route("/removecomment/<int:id>")
def removecomment(id):
    # Fetch the track_id for redirecting:
    sql = "SELECT track_id, user_id FROM Comments WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    track_info = result.fetchone()
    track_id = track_info[0]
    user_id = track_info[1]

    # comment can be removed if:
    # - the userid in session matches the comment or
    # - if session has admin rights
    # maybe pur the 403 last?

    # Check if user session exists
    if "userid" in session:
        # Check for correct userid or admin rights
        if session["userid"] == user_id or session["admin"]:
            # The comment is removed.
            sql = "DELETE FROM Comments WHERE id=:id"
            db.session.execute(text(sql), {"id":id})
            db.session.commit()
            track_url = url_for('track', id=track_id)
            return redirect(track_url)

    # Throw a 403 for the rats trying to slip in >:)
    error.throw(403)

@app.route("/editcomment/<int:id>")
def editcomment(id):
    sql = "SELECT id, content, track_id, user_id FROM Comments WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    comment = result.fetchone()

    if "userid" not in session:
        error.throw(403)
    elif session["userid"] != comment.user_id:
        error.throw(403)

    return render_template("editcomment.html", comment=comment)

@app.route("/sendedit", methods=['POST'])
def sendedit():
    comment_id = request.form["comment_id"]
    newcontent = request.form["editedcomment"]
    trackid = request.form["track_id"]
    sql = "UPDATE Comments SET content=:content WHERE id=:id"
    db.session.execute(text(sql), {"content":newcontent, "id":comment_id})
    db.session.commit()

    track_url = url_for('track', id=trackid)
    return redirect(track_url)
