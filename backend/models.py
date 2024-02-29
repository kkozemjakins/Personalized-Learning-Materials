from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.Text, nullable=False)
    role_id = db.Column(db.Integer, default=0)  # Foreign key relationship
'''
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    role_name = db.Column(db.String(150), unique=True)
    role_description = db.Column(db.String(5000), unique=True)'''

class Profession(db.Model):
    __tablename__ = "professions"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    profession_name = db.Column(db.String(150), unique=True)
    profession_description = db.Column(db.String(5000))