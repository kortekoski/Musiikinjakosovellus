from sqlalchemy.sql import text
from db import db

def get_genres():
    sql = "SELECT * FROM Genres"
    result = db.session.execute(text(sql))
    genres = result.fetchall()
    
    return genres

def get_genretracks(id):
    sql = "SELECT Tracks.id, Tracks.user_id, Tracks.name AS trackname, Tracks.private, Genres.name AS genrename, Genres.id AS genre_id, Users.username from Tracks \
        LEFT JOIN Genres ON Tracks.genre_id=Genres.id \
        LEFT JOIN Users ON Tracks.user_id=Users.id \
        WHERE Tracks.genre_id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    genretracks = result.fetchall()

    return genretracks

def public_count(id):
    sql = "SELECT COUNT(name) FROM Tracks \
            WHERE genre_id=:genreid AND visible=True AND private=False"
    result = db.session.execute(text(sql), {"genreid":id})
    count = result.fetchone()[0]

    return count

def private_count(id):
    sql = "SELECT COUNT(name) FROM Tracks \
            WHERE genre_id=:genreid AND visible=True AND private=True"
    result = db.session.execute(text(sql), {"genreid":id})
    count = result.fetchone()[0]

    return count

def last_uploaded(id):
    sql = "SELECT date FROM Tracks \
                WHERE genre_id=:genreid AND visible=True AND private=False \
                ORDER BY date DESC"
    result = db.session.execute(text(sql), {"genreid":id})    
    last_uploaded = result.fetchone()

    return last_uploaded

def last_uploaded_admin(id):
    sql = "SELECT date FROM Tracks \
                WHERE genre_id=:genreid AND visible=True \
                ORDER BY date DESC"
    result = db.session.execute(text(sql), {"genreid":id})    
    last_uploaded = result.fetchone()

    return last_uploaded