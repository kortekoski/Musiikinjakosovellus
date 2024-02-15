from flask import redirect, render_template, request, session, make_response, url_for
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from db import db
from utils import error
import queries

@app.route("/playlist/<int:id>")
def playlist(id):
    tracks = queries.get_playlist_tracks(id)

    return render_template("playlist.html", tracks=tracks)