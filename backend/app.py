#app.py
from flask import Flask, request, jsonify, session, Response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User, Profession, ProfTest, ProfTestQuestions, ProfTestMarks
import openai
import json
from bs4 import BeautifulSoup
import ast

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)

with app.app_context():
    db.create_all()
    @current_app.before_request
    def basic_authentication():
        if request.method.lower() == 'options':
            return ''

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

with app.app_context():  # Add this to ensure the app context is available
    @current_app.before_request
    def basic_authentication():
        if request.method.lower() == 'options':
            return Response()


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
  
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role_id": user.role_id  # Assuming User model has a role_id field
    })

######
def get_entities(model, entity_name, fields):
    entities = model.query.all()
    entity_list = [{field: getattr(entity, field) for field in fields} for entity in entities]
    print(f"{entity_name} data:", entity_list)
    return jsonify({entity_name: entity_list})


def add_entity(model, request, fields):
    data = {field: request.form.get(field) for field in fields}
    
    entity_exists = model.query.filter_by(**data).first() is not None

    if entity_exists:
        return jsonify({"error": f"This {model.__name__} already exists"}), 409

    new_entity = model(**data)
    db.session.add(new_entity)
    db.session.commit()

    return jsonify({"message": f"{model.__name__} added successfully", "id": new_entity.id})


def handle_delete(model, item_id):
    item = model.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": f"{model.__name__} deleted successfully"})
    else:
        return jsonify({"error": f"{model.__name__} not found"}), 404


def handle_update(model, item_id):
    item = model.query.get(item_id)
    if item:
        new_data = {field: request.json.get(field) for field in model.__table__.columns.keys() if field != 'id' and field != 'password'}
        item.update(new_data)
        return jsonify({"message": f"{model.__name__} modified successfully"})
    else:
        return jsonify({"error": f"{model.__name__} not found"}), 404

######
    

# User adding/viewing/modifying/deleting
@app.route("/get_users", methods=["GET"])
def get_users():
    return get_entities(User, "users", ["id", "email", "role_id"])

@app.route("/add_user", methods=["POST"])
def add_user():
    return add_entity(User, request, ["email", "password", "role_id"])


@app.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    return handle_delete(User, user_id)



@app.route("/update_user/<user_id>", methods=["PUT"])
def update_user(user_id):
    return handle_update(User, user_id)

# Profession test

@app.route("/get_test", methods=["GET"])
def get_tests():
    return get_entities(ProfTest, "profTest", ["id", "profession_id", "question_amount"])

@app.route("/add_test", methods=["POST"])
def add_test():
    return add_entity(ProfTest, request, ["id", "profession_id", "question_amount"])


@app.route("/delete_test/<test_id>", methods=["DELETE"])
def delete_test(test_id):
    return handle_delete(ProfTest, test_id)

@app.route("/update_test/<test_id>", methods=["PUT"])
def update_test(test_id):
    return handle_update(ProfTest, test_id)

# Profession questions 

@app.route("/get_test_questions", methods=["GET"])
def get_tests_questions():
    return get_entities(ProfTestQuestions, "profTestCreatedQuestions", ["id", "prof_test_id", "level_of_question", "question", "correct_answer", "answer_variant1", "answer_variant2", "answer_variant3", "answer_variant4"])

@app.route("/add_test_questions", methods=["POST"])
def add_test_questions():
    return add_entity(ProfTestQuestions, request, ["id", "prof_test_id", "question", "correct_answer"])


@app.route("/delete_test_questions/<test_questions_id>", methods=["DELETE"])
def delete_test_questions(test_questions_id):
    return handle_delete(ProfTestQuestions, test_questions_id)


@app.route("/update_test_questions/<test_id_questions>", methods=["PUT"])
def update_test_questions(test_questions_id):
    return handle_update(ProfTestQuestions, test_questions_id)




# Profession adding/viewing/modifying/deleting
@app.route("/get_prof", methods=["GET"])
def get_prof():
    return get_entities(Profession, "professions", ["id", "profession_name", "profession_description"])

'''@app.route("/add_prof", methods=["POST"])
def add_prof():
    return add_entity(Profession, request, ["profession_name", "profession_description"])'''

@app.route("/add_prof", methods=["POST"])
def add_prof():
    result = add_entity(Profession, request, ["profession_name", "profession_description"])

    # Check if the profession was added successfully
    if "message" in json.loads(result.data):
        # Profession added successfully, now create a test using OpenAI
        profession_name = request.form.get("profession_name")
        profession_description = request.form.get("profession_description")
        
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
        user_request = f"Generate fifteen basic level questions, ten intermediate level questions, and five advanced level questions with answers for the newly added profession - {profession_name}, profession description - {profession_description}. The design should be like this - question number, question, question level in brackets and a list of 4 answer options. And can you output it with JSON array. For each question the question level will have to be written. Also please don't use newline characters and the leading and trailing backticks from the string. Please use this example of output as a template: {json.dumps(user_request_dict)}"
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

        # Log the raw question content
        app.logger.info("Raw question content: " + test_content)

        try:
            test_questions_data = json.loads(test_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": test_content}), 500

        profession_id = json.loads(result.data)["id"]

        # Create a new profession test
        new_test = ProfTest(
            profession_id=profession_id,
            question_amount=len(test_questions_data)
        )
        db.session.add(new_test)
        db.session.commit()

        # Add test questions to the database
        for question_data in test_questions_data["questions"]:
            new_question = ProfTestQuestions(
                prof_test_id=new_test.id,
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

        return jsonify({"message": f"Profession added successfully, and a test has been created with questions."+test_content})

    return result  # Return the entire response, including errors


@app.route("/delete_prof/<prof_id>", methods=["DELETE"])
def delete_prof(prof_id):
    return handle_delete(Profession, prof_id)

@app.route("/update_prof/<prof_id>", methods=["PUT"])
def update_prof(prof_id):
    return handle_update(Profession, prof_id)

if __name__ == "__main__":
    app.run(debug=True)