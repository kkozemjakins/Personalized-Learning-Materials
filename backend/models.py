# models.py
'''
from firestore import initialize_firestore
from uuid import uuid4

db = initialize_firestore()

def get_uuid():
    return uuid4().hex

class User:
    def __init__(self, email, username, password, role_id):
        self.email = email
        self.username = username
        self.password = password
        self.role_id = role_id

class Profession:
    def __init__(self, profession_name, profession_description):
        self.id = get_uuid()
        self.profession_name = profession_name
        self.profession_description = profession_description


class ProfessionKeyPoints:
    def __init__(self, profession_id, key_point, point_desc):
        self.id = get_uuid()
        self.profession_id = db.collection('professions').document(profession_id)
        self.key_point = key_point
        self.point_desc = point_desc



class Test:
    def __init__(self, test_name, profession_id, question_amount):
        self.id = get_uuid()
        self.profession_id = db.collection('professions').document(profession_id)
        self.test_name = test_name
        self.question_amount = question_amount


class TestQuestions:
    def __init__(self, prof_test_id, question, level_of_question, correct_answer, answer_variant1, answer_variant2, answer_variant3, answer_variant4):
        self.id = get_uuid()
        self.prof_test_id = db.collection('Test').document(prof_test_id)
        self.question = question
        self.level_of_question = level_of_question
        self.correct_answer = correct_answer
        self.answer_variant1 = answer_variant1
        self.answer_variant2 = answer_variant2
        self.answer_variant3 = answer_variant3
        self.answer_variant4 = answer_variant4


class TestUserResults:
    def __init__(self, prof_test_id, user_id, user_marks_id, questions_id, user_answer, correct_incorrect):
        self.id = get_uuid()
        self.prof_test_id = db.collection('Test').document(prof_test_id)
        self.user_id = db.collection('Users').document(user_id)
        self.user_marks_id = db.collection('TestMarks').document(user_marks_id)
        self.questions_id = db.collection('TestQuestions').document(questions_id)
        self.user_answer = user_answer
        self.correct_incorrect = correct_incorrect


class TestMarks:
    def __init__(self, prof_test_id, user_id, mark, correct_answers_amount, incorrect_answers_amount, comment_on_results):
        self.id = get_uuid()
        self.prof_test_id = db.collection('Test').document(prof_test_id)
        self.user_id = db.collection('Users').document(user_id)
        self.mark = mark
        self.correct_answers_amount = correct_answers_amount
        self.incorrect_answers_amount = incorrect_answers_amount
        self.comment_on_results = comment_on_results

'''