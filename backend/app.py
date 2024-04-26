# app.py

from flask import Flask, request, jsonify, session, Response, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User, Profession, ProfTest, ProfTestQuestions, ProfTestMarks, ProfTestUserResults
import openai
import json
import os
import glob

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)

class OpenAIChat:
    def __init__(self):
        openai.api_key = "your_openai_api_key"

    def generate_content(self, system_request, user_request):
        try:
            client = openai.ChatCompletion.create(
                model="text-davinci-002",
                messages=[
                    {"role": "system", "content": system_request},
                    {"role": "user", "content": user_request}
                ]
            )
            return client['choices'][0]['message']['content']
        except Exception as e:
            return f"Failed to generate content: {str(e)}"


class DatabaseHandler:
    @staticmethod
    def get_entities(model, entity_name, fields):
        entities = model.query.all()
        entity_list = [{field: getattr(entity, field) for field in fields} for entity in entities]
        print(f"{entity_name} data:", entity_list)
        return jsonify({entity_name: entity_list})

    @staticmethod
    def get_entity_by_id(model, entity_name, fields, entity_id):
        entity = model.query.get(entity_id)
        if entity:
            entity_data = {field: getattr(entity, field) for field in fields}
            print(f"{entity_name} data:", entity_data)
            return jsonify({entity_name: entity_data})
        else:
            return jsonify({"error": f"{entity_name} not found"}), 404

    @staticmethod
    def add_entity(model, request, fields):
        data = {field: request.form.get(field) for field in fields}
        
        entity_exists = model.query.filter_by(**data).first() is not None

        if entity_exists:
            return jsonify({"error": f"This {model.__name__} already exists"}), 409

        new_entity = model(**data)
        db.session.add(new_entity)
        db.session.commit()

        return jsonify({"message": f"{model.__name__} added successfully", "id": new_entity.id})

    @staticmethod
    def handle_delete(model, item_id):
        item = model.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": f"{model.__name__} deleted successfully"})
        else:
            return jsonify({"error": f"{model.__name__} not found"}), 404

    @staticmethod
    def handle_update(model, item_id, new_data):
        item = model.query.get(item_id)
        if item:
            for field, value in new_data.items():
                setattr(item, field, value)
            db.session.commit()
            return jsonify({"message": f"{model.__name__} modified successfully"})
        else:
            return jsonify({"error": f"{model.__name__} not found"}), 404


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/signup", methods=["POST"])
def signup():
    email = request.json["email"]
    password = request.json["password"]
 
    user_exists = User.query.filter_by(email=email).first() is not None
 
    if user_exists:
        return jsonify({"error": "Email already exists"}), 409
     
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
 
    session["user_id"] = new_user.id
 
    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })


@app.route("/logout", methods=["GET"])
def logout_user():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]
  
    user = User.query.filter_by(email=email).first()
  
    if user is None:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
      
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_role"] = user.role_id
  
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role_id": user.role_id,
    })


class ProfTestHandler:
    @staticmethod
    def create_prof_test(system_request, user_request):
        openai_chat = OpenAIChat()
        content = openai_chat.generate_content(system_request, user_request)
        try:
            test_questions_data = json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": content}), 500

        # Add test questions to the database
        for question_data in test_questions_data["questions"]:
            new_question = ProfTestQuestions(
                prof_test_id=prof_test.id,
                question=question_data["question"],
                level_of_question=question_data["question_level"],
                correct_answer=question_data["correct_answer"],
                answer_variant1=question_data["answers"][0],
                answer_variant2=question_data["answers"][1],
                answer_variant3=question_data["answers"][2],
                answer_variant4=question_data["answers"][3]
            )
            db.session.add(new_question)

        db.session.commit()

        return jsonify({"message": f"Profession added successfully, and a test has been created with questions."})


@app.route("/add_prof", methods=["POST"])
def add_prof():
    system_request = "You will be provided with a profession and its description, and on this basis, you will need to create a test that will test knowledge level of junior specialist about the profession main skills, with 30 questions of different levels and answers to them. 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions, in total need to be 30 questions related to lastest skills needed in that junior specialist role."
    user_request = f"Generate 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions with answers for the newly added profession - {request.form.get('profession_name')}, profession description - {request.form.get('profession_description')}. The design should be like this - {{ 'questions': [{{ 'question': 'Question content', 'question_level': 'Basic', 'answers': ['Option 1', 'Option 2', 'Option 3', 'Option 4'], 'correct_answer': 'Correct option'}}]}}"
    return ProfTestHandler.create_prof_test(system_request, user_request)


@app.route("/get_prof")
def get_prof():
    return DatabaseHandler.get_entities(Profession, "Professions", ["id", "profession_name", "profession_description"])


@app.route("/get_prof/<prof_id>")
def get_prof_by_id(prof_id):
    return DatabaseHandler.get_entity_by_id(Profession, "Profession", ["id", "profession_name", "profession_description"], prof_id)


@app.route("/delete_prof/<prof_id>", methods=["DELETE"])
def delete_prof(prof_id):
    return DatabaseHandler.handle_delete(Profession, prof_id)


@app.route("/update_prof/<prof_id>", methods=["PUT"])
def update_prof(prof_id):
    new_data = {"profession_name": request.form.get("profession_name"), "profession_description": request.form.get("profession_description")}
    return DatabaseHandler.handle_update(Profession, prof_id, new_data)

@app.route("/get_test_questions_by_profession/<test_questions_id>")
def get_test_questions_by_profession(test_questions_id):
    return DatabaseHandler.get_entity_by_id(ProfTestQuestions, "ProfTestQuestions", ["id", "prof_test_id", "question","level_of_question", "correct_answer", "answer_variant1", "answer_variant2", "answer_variant3", "answer_variant4"], test_questions_id)


@app.route("/delete_test_questions_by_profession/<test_questions_id>", methods=["DELETE"])
def delete_test_questions_by_profession(test_questions_id):
    return DatabaseHandler.handle_delete(ProfTestQuestions, test_questions_id)


if __name__ == '__main__':
    app.run(debug=True)
