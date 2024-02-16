from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries
from datetime import datetime

@app.route("/comment/<int:track_id>", methods=["POST"])
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

@app.route("/sendedit", methods=["POST"])
def sendedit():
    comment_id = request.form["comment_id"]
    newcontent = request.form["editedcomment"]
    edittime = datetime.now().ctime()
    newcontent += "\nEdited on" + edittime
    trackid = request.form["track_id"]
    sql = "UPDATE Comments SET content=:content WHERE id=:id"
    db.session.execute(text(sql), {"content":newcontent, "id":comment_id})
    db.session.commit()

    track_url = url_for('track', id=trackid)
    return redirect(track_url)