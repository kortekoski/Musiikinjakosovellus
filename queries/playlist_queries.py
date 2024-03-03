from sqlalchemy.sql import text
from db import db

def create_playlist(request):
    playlist_name = request.form.get('playlistname')
    playlist_description = request.form.get('description')
    createsql = "INSERT INTO Playlists (name, description) VALUES (:name, :description)"
    db.session.execute(text(createsql), {"name":playlist_name, "description":playlist_description})
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

def get_playlist(id):
    sql = "SELECT * FROM Playlists WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    playlist = result.fetchone()

    return playlist

def get_playlist_tracks(id):
    sql = "SELECT PlaylistsTracks.track_id, Tracks.name AS trackname, Users.username, Playlists.name AS playlistname \
        FROM PlaylistsTracks \
        LEFT JOIN Playlists ON PlaylistsTracks.playlist_id=Playlists.id \
        LEFT JOIN Tracks ON PlaylistsTracks.track_id=Tracks.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE PlaylistsTracks.playlist_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    tracks = result.fetchall()

    return tracks

def delete_playlist(request):
    playlistid = request.form.get("playlistid")
    sql = "DELETE FROM Playlists WHERE id=:playlistid"
    db.session.execute(text(sql), {"playlistid":playlistid})
    db.session.commit()
    return True

def edit_playlist(request):
    playlistid = request.form.get("playlistid")

    # Change the name and description first, if needed
    originalname = request.form.get("originalname")
    newname = request.form.get("playlistname")
    originaldesc = request.form.get("originaldesc")
    newdesc = request.form.get("description")

    if originalname != newname and originaldesc != newdesc:
        ndsql = "UPDATE Playlists SET name=:newname, description=:newdesc WHERE id=:playlistid"
        db.session.execute(text(ndsql), {"newname":newname, "newdesc":newdesc, "playlistid":playlistid})
        db.session.commit()
    else:
        if originalname != newname:
            namesql = "UPDATE Playlists SET name=:newname WHERE id=:playlistid"
            db.session.execute(text(namesql), {"newname":newname, "playlistid":playlistid})
            db.session.commit()
        
        if originaldesc != newdesc:
            descsql = "UPDATE Playlists SET description=:newdesc WHERE id=:playlistid"
            db.session.execute(text(descsql), {"newdesc":newdesc, "playlistid":playlistid})
            db.session.commit()

    # The junction table is first cleared of instances pertaining to the playlist.
    clearsql = "DELETE FROM PlaylistsTracks WHERE playlist_id=:playlistid"
    db.session.execute(text(clearsql), {"playlistid":playlistid})
    db.session.commit()

    track_ids = request.form.getlist('checked')

    # Now the new ids are inserted.
    # This seems to be the easiest way to edit the connections between playlists and tracks.
    for id in track_ids:
        sql = "INSERT INTO PlaylistsTracks (playlist_id, track_id) \
            VALUES (:pid, :tid)"
        db.session.execute(text(sql), {"pid":playlistid, "tid":id})
        db.session.commit()

    return True