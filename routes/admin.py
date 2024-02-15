from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries

@app.route("/adminpanel")
def adminpanel():
    if session["admin"]:
        return render_template("adminpanel.html")

    return error.throw(403)

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