from app import app
from db import db
from flask import redirect, render_template, request, session, make_response, url_for, abort
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/")
def index():
    sql = "SELECT id, name FROM Genres"
    result = db.session.execute(text(sql))
    genres = result.fetchall()

    info = {}
    for genre in genres:
        genreid = genre.id
        # Get counts of the tracks in each genre (skip invisible and private tracks)
        count = db.session.execute(text("SELECT COUNT(name) FROM Tracks WHERE genre_id=:genreid AND visible=True AND private=False"), {"genreid":genreid}).fetchone()[0]
        # Get the last uploaded track (skip invisible and private tracks)
        last_uploaded = db.session.execute(text("SELECT date FROM Tracks WHERE genre_id=:genreid AND visible=True AND private=False ORDER BY date DESC"), {"genreid":genreid}).fetchone()

        infotuple = (count, last_uploaded)
        info[genreid] = infotuple

    return render_template("index.html", genres=genres, info=info)

# This route is for the search function.
@app.route("/result")
def result():
    query = request.args["query"].lower()
    sql = "SELECT Tracks.id, name, username FROM Tracks \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE LOWER(name) LIKE :query"
    result = db.session.execute(text(sql), {"query":"%"+query+"%"})
    tracks = result.fetchall()
    return render_template("result.html", tracks=tracks)

@app.route("/genre/<int:id>")
def genre(id):
    sql = "SELECT Tracks.id, Tracks.name AS trackname, Tracks.visible, Tracks.private, Genres.name AS genrename, Genres.id AS genre_id, Users.username from Tracks \
        LEFT JOIN Genres ON Tracks.genre_id=Genres.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id\
        WHERE Tracks.genre_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    genretracks = result.fetchall()
    return render_template("genre.html", genretracks=genretracks)

@app.route("/profile/<int:id>")
def profile(id):
    sql = "SELECT Users.id AS userid, Users.username, Tracks.id AS trackid, Tracks.name, Tracks.visible, Tracks.private FROM Users LEFT JOIN Tracks ON Users.id=Tracks.user_id WHERE Users.id=:id"
    result = db.session.execute(text(sql), {"id":id})
    tracks = result.fetchall()
    return render_template("profile.html", id=id, tracks=tracks)

@app.route("/deletetrack", methods=["POST"])
def deletetrack():
    if not session["admin"]:
        redirect("/")

    # The track isn't really deleted, only turned invisible.
    trackid = request.form["trackid"]
    genreid = request.form["genreid"]
    sql = "UPDATE Tracks SET visible=False WHERE id=:trackid"
    db.session.execute(text(sql), {"trackid":trackid})
    db.session.commit()
    genreurl = url_for('genre', id=genreid)
    return redirect(genreurl)

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
def test():
    sql = "SELECT * FROM Genres"
    result = db.session.execute(text(sql))
    genres = result.fetchall()
    print(genres)
    return render_template("upload.html", genres=genres)

@app.route("/send", methods=['POST'])
def upload():
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

@app.route("/edittrack/<int:id>")
def edittrack(id):
    sql = "SELECT Tracks.id AS trackid, name, genre_id, description, private, Users.id AS userid FROM Tracks LEFT JOIN Users ON Tracks.user_id=Users.id WHERE Tracks.id=:id"
    result = db.session.execute(text(sql), {"id":id})
    trackinfo = result.fetchone()

    if "userid" not in session:
        abort(403, "Access forbidden: You do not have permission to access this resource.")
    elif session["userid"] != trackinfo.userid:
        abort(403, "Access forbidden: You do not have permission to access this resource.")
    
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
@app.route("/play/<int:id>")
def play(id):
    track_sql = "SELECT data FROM Tracks where id=:id"
    result = db.session.execute(text(track_sql), {"id":id})
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

    # Fetch the comments for the track:
    comment_sql = "SELECT user_id, Comments.id, content, date, username FROM Comments LEFT JOIN Users on Comments.user_id=Users.id WHERE track_id=:id"
    result = db.session.execute(text(comment_sql), {"id":id})
    comments = result.fetchall()

    return render_template("track.html", track=track, comments=comments)

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
    track_id = result.fetchone()[0]

    if "userid" not in session:
        abort(403, "Access forbidden: You do not have permission to access this resource.")
    elif session["userid"] != comment.user_id:
        abort(403, "Access forbidden: You do not have permission to access this resource.")

    # The comment is removed.
    sql = "DELETE FROM Comments WHERE id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()

    track_url = url_for('track', id=track_id)
    return redirect(track_url)

@app.route("/editcomment/<int:id>")
def editcomment(id):
    sql = "SELECT id, content, track_id, user_id FROM Comments WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    comment = result.fetchone()

    if "userid" not in session:
        abort(403, "Access forbidden: You do not have permission to access this resource.")
    elif session["userid"] != comment.user_id:
        abort(403, "Access forbidden: You do not have permission to access this resource.")

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