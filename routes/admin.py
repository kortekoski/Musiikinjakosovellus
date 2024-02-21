from flask import redirect, render_template, request, session
from app import app
from utils import error
from queries import admin_queries
from utils.check_session import check_csrf

@app.route("/adminpanel")
def adminpanel():
    if session["admin"]:
        return render_template("adminpanel.html")

    return error.throw(403)

@app.route("/addtospotlight", methods=["POST"])
def addtospotlight():
    check_csrf(request)

    if session["admin"]:
        trackid = request.form.get("trackid")
        admin_queries.add_to_spotlight(trackid)
        return redirect('/')
    
    return error.throw(403)

@app.route("/removespotlight", methods=["POST"])
def removespotlight():
    check_csrf(request)

    if session["admin"]:
        trackid = request.form.get("strackid")
        print(trackid)
        admin_queries.remove_from_spotlight(trackid)
        return redirect('/')

    return error.throw(403)