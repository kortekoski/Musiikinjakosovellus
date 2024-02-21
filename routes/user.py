from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from queries import user_queries

@app.before_request
def update_session_current_url():
    """This essentially exists so that redirection to the previous page works after login."""
    session["current_url"] = request.url

@app.route("/profile/<int:id>")
def profile(id):
    tracks = user_queries.get_usertracks(id)
    return render_template("profile.html", id=id, tracks=tracks)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = user_queries.get_user(username)

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
    user_queries.create_user(username, hash_value, admin)
    return "Signup successful, redirecting to index in 3 seconds...", {"Refresh": "3; url=/"}

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    session["admin"] = False
    return redirect("/")