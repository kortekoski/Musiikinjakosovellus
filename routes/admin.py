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
        sql = "INSERT INTO Spotlight (track_id) VALUES (:trackid)"
        db.session.execute(text(sql), {"trackid":trackid})
        db.session.commit()
        return redirect('/')
    
    return error.throw(403)