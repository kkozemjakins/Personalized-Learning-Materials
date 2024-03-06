#models.py
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class BaseMixin:
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, new_data):
        for field, value in new_data.items():
            setattr(self, field, value)
        db.session.commit()

class User(db.Model, BaseMixin):
    __tablename__ = "users"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(150), unique=True)
    #username = db.Column(db.String(150)) 
    password = db.Column(db.Text, nullable=False)
    role_id = db.Column(db.Integer, default=0)  # Foreign key relationship
'''
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    role_name = db.Column(db.String(150), unique=True)
    role_description = db.Column(db.String(5000), unique=True)'''

class Profession(db.Model, BaseMixin):
    __tablename__ = "professions"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    profession_name = db.Column(db.String(150), unique=True)
    profession_description = db.Column(db.String(5000))


class ProfTest(db.Model, BaseMixin):
    __tablename__ = "profTest"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    profession_id = db.Column(db.String(11), db.ForeignKey('professions.id'), unique=True)
    question_amount = db.Column(db.Integer, default=30)


class ProfTestQuestions(db.Model, BaseMixin):
    __tablename__ = "profTestQuestions"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    prof_test_id = db.Column(db.String(11), db.ForeignKey('profTest.id'))
    question = db.Column(db.Text, unique=True)
    type_of_question = db.Column(db.String(150))
    correct_answer = db.Column(db.String(150))

class ProfTestMarks(db.Model, BaseMixin):
    __tablename__ = "profTestMarks"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    prof_test_id = db.Column(db.String(11), db.ForeignKey('profTest.id'))
    user_id = db.Column(db.String(11), db.ForeignKey('users.id'))
    mark = db.Column(db.Integer)
    correct_answers_amount = db.Column(db.Integer)
    incorect_answers_amount = db.Column(db.Integer)




    