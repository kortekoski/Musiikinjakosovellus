from sqlalchemy.sql import text
from db import db

def get_tracks():
    sql = "SELECT * FROM Tracks WHERE visible=True"
    result = db.session.execute(text(sql))
    tracks = result.fetchall()

    return tracks

def get_public_tracks():
    sql = "SELECT * FROM Tracks WHERE visible=True AND private=False"
    result = db.session.execute(text(sql))
    tracks = result.fetchall()

    return tracks

def get_track(id):
    sql = "SELECT * FROM Tracks WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    track = result.fetchone()

    return track

def get_trackinfo(id):
    sql = "SELECT Tracks.id AS trackid, name, genre_id, description, private, Users.id AS userid FROM Tracks LEFT JOIN Users ON Tracks.user_id=Users.id WHERE Tracks.id=:id"
    result = db.session.execute(text(sql), {"id":id})
    trackinfo = result.fetchone()

    return trackinfo

def get_track_comments(id):
    comment_sql = "SELECT user_id, Comments.id, content, date, username FROM Comments LEFT JOIN Users on Comments.user_id=Users.id WHERE track_id=:id ORDER BY date DESC"
    result = db.session.execute(text(comment_sql), {"id":id})
    comments = result.fetchall()

    return comments

def get_data(track_id, version_id):
    if version_id == 0:
        sql = "SELECT data FROM Tracks WHERE id=:track_id"
    elif version_id > 0:
        sql = "SELECT data FROM Versions \
            WHERE track_id=:track_id AND version_number=:version_id"

    result = db.session.execute(text(sql), {"track_id":track_id, "version_id":version_id})
    data = result.fetchone()[0]

    return data

def max_trackid():
    return db.session.execute(text("SELECT MAX(id) FROM Tracks")).fetchone()[0]

def add_track(name, userid, genreid, data, description, private, sharecode):
    sql = "INSERT INTO Tracks (name, user_id, genre_id, date, data, description, private, sharecode) \
        VALUES (:name, :userid, :genreid, NOW(), :data, :description, :private, :sharecode)"
    db.session.execute(text(sql), {"name":name, "userid":userid, "genreid":genreid, "data":data, "description":description, "private":private, "sharecode":sharecode})
    db.session.commit()

def delete_track(id):
    sql = "UPDATE Tracks SET visible=False WHERE id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()

def edit_track(name, genre_id, description, private, track_id):
    sql = "UPDATE Tracks SET name=:name, genre_id=:genre_id, description=:description, private=:private WHERE id=:trackid"
    db.session.execute(text(sql), {"name":name, "genre_id":genre_id, "description":description, "private":private, "trackid":track_id})
    db.session.commit()

def get_versions(id):
    sql = "SELECT * FROM Versions WHERE track_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    versions = result.fetchall()

    return versions

def add_version(id, data, changelog):
    # The version number is determined by fetching versions with the correct
    # track id and adding one. The original becomes "version 0".
    version_count = db.session.execute(text("SELECT COUNT(id) FROM Versions \
            WHERE track_id=:trackid"), \
            {"trackid":id}).fetchone()[0]
    version_number = version_count + 1

    sql = "INSERT INTO Versions (version_number, track_id, data, changelog) \
        VALUES (:version_number, :trackid, :data, :changelog)"
    db.session.execute(text(sql), {"version_number":version_number, "trackid":id, "data":data, "changelog":changelog})
    db.session.commit()

def add_keywords(keywords, id=0):
    # If id=0, there is no given id since the track has just been added to the database.
    # Thus we fetch the largest (latest) id.
    if id==0:
        trackid = db.session.execute(text("SELECT MAX(id) FROM Tracks")).fetchone()[0]
    else:
        trackid = id

    # Clear the previous keywords first:
    db.session.execute(text("DELETE FROM KeywordsTracks WHERE track_id=:trackid"), {"trackid":trackid})
    db.session.commit()

    for keyword in keywords:
        # If the keywords exists in the database, we use the existing id.
        kidsql = "SELECT id FROM Keywords WHERE content=:keyword"
        keywordid = db.session.execute(text(kidsql), {"keyword":keyword}).fetchone()
        if keywordid:
            sql = "INSERT INTO KeywordsTracks (keyword_id, track_id) VALUES (:keywordid, :trackid)"
            db.session.execute(text(sql), {"keywordid":keywordid[0], "trackid":trackid})
            db.session.commit()
        else:
            sql = "INSERT INTO Keywords (content) VALUES (:keyword)"
            db.session.execute(text(sql), {"keyword":keyword})
            db.session.commit()
            keywordid = db.session.execute(text("SELECT MAX(id) FROM Keywords")).fetchone()[0]

            sql = "INSERT INTO KeywordsTracks (keyword_id, track_id) VALUES (:keywordid, :trackid)"
            db.session.execute(text(sql), {"keywordid":keywordid, "trackid":trackid})
            db.session.commit()
        
def get_keywords(id):
    """Gets the keywords attached to the given trackid."""
    sql = "SELECT content FROM Keywords \
        LEFT JOIN KeywordsTracks ON Keywords.id=KeywordsTracks.keyword_id \
        WHERE track_id=:id"

    result = db.session.execute(text(sql), {"id":id})
    keywords = result.fetchall()

    return keywords

def search(query):
    sql = "SELECT Tracks.id, name, username FROM Tracks \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        LEFT JOIN KeywordsTracks ON Tracks.id=KeywordsTracks.track_id \
        LEFT JOIN Keywords ON Keywordstracks.keyword_id=Keywords.id \
        WHERE (LOWER(name) LIKE :query OR LOWER(content) LIKE :query) \
        AND visible=True\
        AND private=False"
    result = db.session.execute(text(sql), {"query":"%"+query+"%"})
    tracks = result.fetchall()

    return tracks

def get_spotlight():
    sql = "SELECT Spotlight.track_id, Tracks.name, Users.username FROM Spotlight \
        LEFT JOIN Tracks ON Spotlight.track_id=Tracks.id \
        LEFT JOIN Users ON Users.id=Tracks.user_id \
        WHERE Tracks.visible=True"
    result = db.session.execute(text(sql))
    spotlight = result.fetchall()

    return spotlight