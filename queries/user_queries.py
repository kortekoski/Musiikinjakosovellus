from sqlalchemy.sql import text
from db import db

def get_usertracks(id):
    sql = "SELECT Users.id AS userid, Users.username, Tracks.id AS trackid, \
        Tracks.name, Tracks.private \
        FROM Users LEFT JOIN Tracks ON Users.id=Tracks.user_id \
        WHERE Users.id=:id AND Tracks.visible=True"
    result = db.session.execute(text(sql), {"id":id})
    usertracks = result.fetchall()

    return usertracks

def get_user(username):
    sql = "SELECT id, password, admin FROM Users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()

    return user

def get_user_byid(id):
    sql = "SELECT username FROM Users WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    user = result.fetchone()

    return user

def create_user(username, hash_value, admin):
    sql = "INSERT INTO Users (username, password, admin) VALUES (:username, :password, :admin)"
    db.session.execute(text(sql), {"username":username, "password":hash_value, "admin":admin})
    db.session.commit()

def user_in_db(username):
    sql = "SELECT * FROM Users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()

    if user:
        return True
    else:
        return False