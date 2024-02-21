from flask import redirect, render_template, request, session, url_for
from app import app
from utils import error
from utils.check_session import check_csrf
from queries import comment_queries

@app.route("/comment/<int:track_id>", methods=["POST"])
def comment(track_id):
    comment_text = request.form["newcomment"]
    user_id = session["userid"]
    comment_queries.add_comment(comment_text, track_id, user_id)

    track_url = url_for('track', id=track_id)
    return redirect(track_url)

@app.route("/removecomment/<int:id>")
def removecomment(id):
    check_csrf(request)

    # Fetch the track_id for redirecting:
    comment = comment_queries.get_comment(id)
    track_id = comment[3]
    user_id = comment[4]

    # comment can be removed if:
    # - the userid in session matches the comment or
    # - if session has admin rights
    # maybe pur the 403 last?

    # Check if user session exists
    if "userid" in session:
        # Check for correct userid or admin rights
        if session["userid"] == user_id or session["admin"]:
            # The comment is removed.
            comment_queries.remove_comment(id)
            track_url = url_for('track', id=track_id)
            return redirect(track_url)

    # Throw a 403 for the rats trying to slip in >:)
    error.throw(403)

@app.route("/editcomment/<int:id>")
def editcomment(id):
    comment = comment_queries.get_comment(id)

    if "userid" not in session:
        error.throw(403)
    elif session["userid"] != comment.user_id:
        error.throw(403)

    return render_template("editcomment.html", comment=comment)

@app.route("/sendedit", methods=["POST"])
def sendedit():
    check_csrf(request)

    comment_id = request.form["comment_id"]
    new_content = request.form["editedcomment"]
    comment_queries.edit_comment(new_content, comment_id)

    trackid = request.form["track_id"]
    track_url = url_for('track', id=trackid)
    return redirect(track_url)