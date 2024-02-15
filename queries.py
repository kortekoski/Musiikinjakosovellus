from sqlalchemy.sql import text
from db import db

def get_tracks():
    sql = "SELECT * FROM Tracks WHERE visible=True"
    result = db.session.execute(text(sql))
    tracks = result.fetchall()

    return tracks

def create_playlist(request):
    playlist_name = request.form.get('playlistname')
    createsql = "INSERT INTO Playlists (name) VALUES (:name)"
    db.session.execute(text(createsql), {"name":playlist_name})
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

def get_playlists():
    sql = "SELECT * FROM Playlists"
    result = db.session.execute(text(sql))
    playlists = result.fetchall()

    return playlists

def get_playlist_tracks(id):
    # need: trackid, trackname, username, playlistname
    sql = "SELECT PlaylistsTracks.track_id, Tracks.name AS trackname, Users.username, Playlists.name AS playlistname \
        FROM PlaylistsTracks \
        LEFT JOIN Playlists ON PlaylistsTracks.playlist_id=Playlists.id \
        LEFT JOIN Tracks ON PlaylistsTracks.track_id=Tracks.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE PlaylistsTracks.playlist_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    tracks = result.fetchall()

    return tracks