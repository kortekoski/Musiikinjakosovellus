from sqlalchemy.sql import text
from db import db

def get_tracks():
    sql = "SELECT * FROM Tracks WHERE visible=True"
    result = db.session.execute(text(sql))
    tracks = result.fetchall()

    return tracks

def create_playlist(request):
    createsql = "INSERT INTO Playlists DEFAULT VALUES"
    db.session.execute(text(createsql))
    db.session.commit()

    idsql = "SELECT MAX(id) FROM Playlists"
    idresult = db.session.execute(text(idsql))
    playlistid = idresult.fetchone()[0]

    track_ids = request.form.getlist('checked')

    for id in track_ids:
        sql = "INSERT INTO PlaylistsTracks (playlist_id, track_id) \
            VALUES (:pid, :tid)"
        db.session.execute(text(sql), {"pid":playlistid, "tid":id})
        db.session.commit()

    return True