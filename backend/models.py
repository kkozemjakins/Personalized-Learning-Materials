#models.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    test_results = db.relationship('ProfTestMarks', backref='user') 

class Profession(db.Model, BaseMixin):
    __tablename__ = "professions"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    profession_name = db.Column(db.String(150), unique=True)
    profession_description = db.Column(db.Text)
    # Define relationships with cascade behavior
    tests = db.relationship('ProfTest', backref='profession', cascade='all, delete')

class ProfTest(db.Model, BaseMixin):
    __tablename__ = "profTest"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    profession_id = db.Column(db.String(11), db.ForeignKey('professions.id'), unique=True)
    question_amount = db.Column(db.Integer, default=30)
    # Define relationships with cascade behavior
    test_questions = db.relationship('ProfTestQuestions', backref='test', cascade='all, delete')
    test_results = db.relationship('ProfTestMarks', backref='test', cascade='all, delete')

class ProfTestQuestions(db.Model, BaseMixin):
    __tablename__ = "profTestCreatedQuestions"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    prof_test_id = db.Column(db.String(11), db.ForeignKey('profTest.id'))
    question = db.Column(db.Text)
    level_of_question = db.Column(db.String(150))
    correct_answer = db.Column(db.String(150))
    answer_variant1 = db.Column(db.String(150))
    answer_variant2 = db.Column(db.String(150))
    answer_variant3 = db.Column(db.String(150))
    answer_variant4 = db.Column(db.String(150))

class ProfTestMarks(db.Model, BaseMixin):
    __tablename__ = "profTestResultsMarksComments"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    prof_test_id = db.Column(db.String(11), db.ForeignKey('profTest.id'))
    user_id = db.Column(db.String(11), db.ForeignKey('users.id'))
    mark = db.Column(db.Integer)
    correct_answers_amount = db.Column(db.Integer)
    incorrect_answers_amount = db.Column(db.Integer)
    comment_on_results = db.Column(db.Text)

class ProfTestUserResults(db.Model, BaseMixin):
    __tablename__ = "profTestUserQA"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    prof_test_id = db.Column(db.String(11), db.ForeignKey('profTest.id'))
    user_id = db.Column(db.String(11), db.ForeignKey('users.id'))
    user_marks_id = db.Column(db.String(11), db.ForeignKey('profTestResultsMarksComments.id'))
    questions_id = db.Column(db.String(11), db.ForeignKey('profTestCreatedQuestions.id'))
    user_answer = db.Column(db.String(150))
    correct_incorrect = db.Column(db.Integer) # 1 if answer was correct, 0 if it was incorrect
