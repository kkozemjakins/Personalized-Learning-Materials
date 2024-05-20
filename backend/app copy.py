# app.py

from flask import Flask, request, jsonify, session, Response, current_app, send_file
from firestore import initialize_firestore
from models import User, Profession, ProfTest, ProfTestQuestions, ProfTestMarks, ProfTestUserResults
import openai
import json
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
import glob

app = Flask(__name__)

# Initialize Firestore
db = initialize_firestore()

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# CORS setup
CORS(app)

with app.app_context():  # Add this to ensure the app context is available
    @current_app.before_request
    def basic_authentication():
        if request.method.lower() == 'options':
            return Response()

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/signup", methods=["POST"])
def signup():
    email = request.json["email"]
    password = request.json["password"]
 
    user_exists = db.collection('users').where("email", "==", email).get()
 
    if user_exists:
        return jsonify({"error": "Email already exists"}), 409
     
    new_user_ref = db.collection('users').add({
        "email": email,
        "password": password
    })

    session["user_id"] = new_user_ref.id
 
    return jsonify({
        "id": new_user_ref.id,
        "email": email
    })

@app.route("/logout", methods=["GET"])
def logout_user():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]
  
    user = db.collection('users').where("email", "==", email).get()
  
    if not user:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    for doc in user:
        user_data = doc.to_dict()
        if user_data["password"] == password:
            session["user_id"] = doc.id
            session["user_email"] = user_data["email"]
            session["user_role"] = user_data.get("role_id", "")
            return jsonify({
                "id": doc.id,
                "email": user_data["email"],
                "role_id": user_data.get("role_id", "")
            })

    return jsonify({"error": "Unauthorized"}), 401

def get_entities(collection, entity_name, fields):
    entities = collection.stream()
    entity_list = [{field: entity.get(field) for field in fields} for entity in entities]
    print(f"{entity_name} data:", entity_list)
    return jsonify({entity_name: entity_list})

def get_entity_by_id(collection, entity_name, fields, entity_id):
    entity = collection.document(entity_id).get()
    if entity.exists:
        entity_data = {field: entity.get(field) for field in fields}
        print(f"{entity_name} data:", entity_data)
        return jsonify({entity_name: entity_data})
    else:
        return jsonify({"error": f"{entity_name} not found"}), 404

def add_entity(collection, data):
    new_entity_ref = collection.add(data)
    return jsonify({"message": f"Document added successfully with ID: {new_entity_ref.id}"})


def delete_entity(collection, entity_id):
    entity = collection.document(entity_id).get()
    if entity.exists:
        collection.document(entity_id).delete()
        return jsonify({"message": f"Document with ID: {entity_id} deleted successfully"})
    else:
        return jsonify({"error": f"Document with ID: {entity_id} not found"}), 404

def update_entity(collection, entity_id, data):
    entity = collection.document(entity_id).get()
    if entity.exists:
        collection.document(entity_id).update(data)
        return jsonify({"message": f"Document with ID: {entity_id} updated successfully"})
    else:
        return jsonify({"error": f"Document with ID: {entity_id} not found"}), 404

@app.route("/get_user/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    return get_entity_by_id(db.collection('users'), "user", ["email", "role_id"], user_id)

@app.route("/get_users", methods=["GET"])
def get_users():
    return get_entities(db.collection('users'), "users", ["email", "role_id"])

@app.route("/add_user", methods=["POST"])
def add_user():
    data = {
        "email": request.json["email"],
        "password": request.json["password"],
        "role_id": request.json.get("role_id", "")
    }
    return add_entity(db.collection('users'), data)

@app.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    return delete_entity(db.collection('users'), user_id)

@app.route("/update_user/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = {
        "email": request.json.get("email"),
        "password": request.json.get("password"),
        "role_id": request.json.get("role_id")
    }
    return update_entity(db.collection('users'), user_id, data)

@app.route("/get_prof", methods=["GET"])
def get_prof():
    return get_entities(db.collection('professions'), "professions", ["profession_name", "profession_description"])


@app.route("/get_prof/<prof_id>")
def get_prof_by_id(prof_id):
    return get_entity_by_id(db.collection('professions'), "profession", ["profession_name", "profession_description"], prof_id)

@app.route("/add_prof", methods=["POST"])
def add_prof():
    data = {
        "profession_name": request.json["profession_name"],
        "profession_description": request.json["profession_description"]
    }
    new_prof_ref = db.collection('professions').add(data)

    # Check if the profession was added successfully
    if new_prof_ref:
        # Profession added successfully, now create a test using OpenAI
        profession_name = request.json["profession_name"]
        profession_description = request.json["profession_description"]
        
        user_request_dict = {
            "questions": [{
                "question_number": 1,
                "question": "What is the main area of expertise for a Full Stack Developer as described in the profession description?",
                "question_level": "basic",
                "answers": ["Mobile Development", "JVM related technologies", "Data Analysis"], 
                "correct_answer": "Cybersecurity"
            }]
        }

        # Customize the OpenAI chat completions creation based on your requirements
        system_request = "You will be provided with a profession and its description, and on this basis, you will need to create a test that will test knowledge level of junior specialist about the profession main skills, with 30 questions of different levels and answers to them. 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions, in total need to be 30 questions related to lastest skills needed in that junior  specialist role."
        user_request = f"Generate 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions with answers for the newly added profession - {profession_name}, profession description - {profession_description}. The design should be like this - question number, question, question level in brackets and a list of 4 answer options. And can you output it with JSON array. For each question the question level will have to be written. Also please don't use newline characters and the leading and trailing backticks from the string. Please use this example of output as a template: {json.dumps(user_request_dict)}"
        client = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": user_request}
            ]
        )

        # Extract test details from OpenAI response
        # Assuming that the response contains a 'choices' field
        test_content = client['choices'][0]['message']['content']

        try:
            test_questions_data = json.loads(test_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": test_content}), 500

        # Create a new profession test
        new_test_ref = db.collection('profTests').add({
            "profession_id": new_prof_ref.id,
            "question_amount": len(test_questions_data["questions"])
        })

        # Add test questions to the database
        for question_data in test_questions_data["questions"]:
            db.collection('profTestQuestions').add({
                "prof_test_id": new_test_ref.id,
                "question": question_data["question"],
                "level_of_question": question_data["question_level"],
                "correct_answer": question_data["correct_answer"],
                "answer_variant1": question_data["answers"][0],
                "answer_variant2": question_data["answers"][1],
                "answer_variant3": question_data["answers"][2],
                "answer_variant4": question_data["answers"][3]
            })

        return jsonify({"message": f"Profession added successfully, and a test has been created with questions. Test content: {test_content}"})

    return jsonify({"error": "Failed to add profession"}), 500

@app.route("/delete_prof/<prof_id>", methods=["DELETE"])
def delete_prof(prof_id):
    return delete_entity(db.collection('professions'), prof_id)

@app.route("/update_prof/<prof_id>", methods=["PUT"])
def update_prof(prof_id):
    data = {
        "profession_name": request.json.get("profession_name"),
        "profession_description": request.json.get("profession_description")
    }
    return update_entity(db.collection('professions'), prof_id, data)

@app.route("/get_test", methods=["GET"])
def get_tests():
    return get_entities(db.collection('profTests'), "profTests", ["profession_id", "question_amount"])

@app.route("/add_test", methods=["POST"])
def add_test():
    data = {
        "profession_id": request.json["profession_id"],
        "question_amount": request.json["question_amount"]
    }
    return add_entity(db.collection('profTests'), data)

@app.route("/delete_test/<test_id>", methods=["DELETE"])
def delete_test(test_id):
    return delete_entity(db.collection('profTests'), test_id)

@app.route("/update_test/<test_id>", methods=["PUT"])
def update_test(test_id):
    data = {
        "profession_id": request.json.get("profession_id"),
        "question_amount": request.json.get("question_amount")
    }
    return update_entity(db.collection('profTests'), test_id, data)

@app.route("/get_test_questions_by_profession/<profession_id>", methods=["GET"])
def get_test_questions_by_profession(profession_id):
    try:
        profession = db.collection('professions').document(profession_id).get()
        if not profession.exists:
            return jsonify({'error': 'Profession not found'}), 404

        prof_tests = db.collection('profTests').where("profession_id", "==", profession_id).stream()
        test_questions = []
        for prof_test in prof_tests:
            questions = db.collection('profTestQuestions').where("prof_test_id", "==", prof_test.id).stream()
            for question in questions:
                test_questions.append({
                    'question_id': question.id,
                    'question': question.get("question"),
                    'question_level': question.get("level_of_question"),
                    'correct_answer': question.get("correct_answer"),
                    'answer_variant1': question.get("answer_variant1"),
                    'answer_variant2': question.get("answer_variant2"),
                    'answer_variant3': question.get("answer_variant3"),
                    'answer_variant4': question.get("answer_variant4"),
                })

        return jsonify(test_questions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
