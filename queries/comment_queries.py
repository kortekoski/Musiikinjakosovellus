from sqlalchemy.sql import text
from db import db

def add_comment(content, track_id, user_id):
    sql = "INSERT INTO Comments (content, date, track_id, user_id) \
        VALUES (:content, NOW(), :id, :userid)"
    db.session.execute(text(sql), {"content":content, "id":track_id, "userid":user_id})
    db.session.commit()

def get_comment(id):
    sql = "SELECT * FROM Comments WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    comment = result.fetchone()
    return comment

def remove_comment(id):
    sql = "DELETE FROM Comments WHERE id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()

def edit_comment(new_content, id):
    sql = "UPDATE Comments SET content=:content WHERE id=:id"
    db.session.execute(text(sql), {"content":new_content, "id":id})
    db.session.commit()