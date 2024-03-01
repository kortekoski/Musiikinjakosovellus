from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from queries import user_queries
from utils import error
import secrets

@app.before_request
def update_session_current_url():
    """This exists so that redirection to the previous page works after login."""
    if "styles.css" not in request.url and "login" not in request.url and "signup" not in request.url:
        session["current_url"] = request.url

@app.route("/profile/<int:id>")
def profile(id):
    user = user_queries.get_user_byid(id)

    if not user:
        error.throw(404)

    username = user[0]
    tracks = user_queries.get_usertracks(id)
    return render_template("profile.html", id=id, tracks=tracks, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    previous_url = session["current_url"]
    if not previous_url:
        previous_url = url_for('/')
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = user_queries.get_user(username)

        if not user:
            return redirect(url_for('login', error='Invalid username'))
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                session["username"] = username
                session["userid"] = user.id
                session["admin"] = user.admin
                session["csrf_token"] = secrets.token_hex(16)

                return redirect(previous_url)
            else:
                return redirect(url_for('login', error='Invalid password'))

    return render_template("login.html", error=request.args.get('error'), previous_url = request.args.get('previous_url'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ## Validation checklist:

        ## No empty username or password
        if not username:
            return redirect(url_for('signup', error='Insert a username!'))
        
        if not password:
            return redirect(url_for('signup', error='Insert a password!'))
        
        ## Username must be unique
        if user_queries.user_in_db(username):
            return redirect(url_for('signup', error='Username already in use!'))

        admin = request.form["admin"]
        hash_value = generate_password_hash(password)
        user_queries.create_user(username, hash_value, admin)
        new_user = user_queries.get_user(username)
        session["username"] = username
        session["userid"] = new_user.id
        session["admin"] = new_user.admin
        session["csrf_token"] = secrets.token_hex(16)
        
        return "Signup successful, logging in and redirecting to index in 3 seconds...", {"Refresh": "3; url=/"}

    return render_template("signup.html", error=request.args.get('error'))

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    del session["csrf_token"]
    session["admin"] = False

    return redirect("/")