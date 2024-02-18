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

@app.route("/addtospotlight", methods=["POST"])
def addtospotlight():
    if session["admin"]:
        trackid = request.form.get("trackid")
        queries.add_to_spotlight(trackid)
        return redirect('/')
    
    return error.throw(403)

@app.route("/removespotlight", methods=["POST"])
def removespotlight():
    if session["admin"]:
        trackid = request.form.get("strackid")
        print(trackid)
        queries.remove_from_spotlight(trackid)
        return redirect('/')

    return error.throw(403)