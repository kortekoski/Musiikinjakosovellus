from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries

@app.before_request
def update_session_current_url():
    """This essentially exists so that redirection to the previous page works after login."""
    session["current_url"] = request.url

@app.route("/profile/<int:id>")
def profile(id):
    sql = "SELECT Users.id AS userid, Users.username, Tracks.id AS trackid, \
        Tracks.name, Tracks.private \
        FROM Users LEFT JOIN Tracks ON Users.id=Tracks.user_id \
        WHERE Users.id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    tracks = result.fetchall()
    return render_template("profile.html", id=id, tracks=tracks)


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

                return redirect(request.form["redirect_url"])
            else:
                error = 'Invalid password!'
                return redirect(url_for('login', error='Invalid password'))

    return render_template("login.html", error=request.args.get('error'), previous_url = request.args.get('previous_url'))

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/registeruser", methods=["POST"])
def registeruser():
    username = request.form["username"]
    password = request.form["password"]
    admin = request.form["admin"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO Users (username, password, admin) VALUES (:username, :password, :admin)"
    db.session.execute(text(sql), {"username":username, "password":hash_value, "admin":admin})
    db.session.commit()
    return "Signup successful, redirecting to index in 3 seconds...", {"Refresh": "3; url=/"}

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    session["admin"] = False
    return redirect("/")