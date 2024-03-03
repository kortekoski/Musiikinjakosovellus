from sqlalchemy.sql import text
from db import db

def add_to_spotlight(id):
    sql = "INSERT INTO Spotlight (track_id) VALUES (:trackid)"
    db.session.execute(text(sql), {"trackid":id})
    db.session.commit()

def remove_from_spotlight(id):
    sql = "DELETE FROM Spotlight WHERE track_id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()

def add_genre(name):
    sql = "INSERT INTO Genres (name) VALUES (:name)"
    db.session.execute(text(sql), {"name":name})
    db.session.commit()