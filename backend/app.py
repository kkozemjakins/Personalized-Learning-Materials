#app.py
from flask import Flask, request, jsonify, session, Response, current_app
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User, Profession, ProfTest, ProfTestQuestions, ProfTestMarks
from openai import OpenAI
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

bcrypt = Bcrypt(app)
CORS(app)
db.init_app(app)

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
    return get_entities(ProfTestQuestions, "profTestQuestions", ["id", "prof_test_id", "question", "correct_answer"])

@app.route("/add_test_questions", methods=["POST"])
def add_test_questions():
    return add_entity(ProfTestQuestions, request, ["id", "prof_test_id", "question", "correct_answer"])


@app.route("/delete_test_questions/<test_id_questions>", methods=["DELETE"])
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
 
        # Customize the OpenAI chat completions creation based on your requirements
        system_request = "You will be provided with a profession and its description, and on this basis, you will need to create a test that will test knowledge about the profession, with 30 questions of different levels and answers to them(list correct answer in the end with the number of questions). 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions, in total need to be 30 questions. The design should be like this - question number, question, question level in brackets and a list of 4 answer options, to the right of the correct answer there should be a '*' symbol"
        user_request = f"Generate test questions with answers for the newly added profession - {profession_name}, profession description - {profession_description}"
 
        client = OpenAI()
 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": user_request}
            ]
        )
 
        # Extract test details from OpenAI response
        test_questions = []
        if 'choices' in completion and len(completion['choices']) > 0:
            first_choice = completion['choices'][0]
            if 'message' in first_choice and 'content' in first_choice['message']:
                test_questions = first_choice['message']['content']
 
        # Save test details in the database
        new_test = ProfTest(profession_id=json.loads(result.data)["id"])

        db.session.add(new_test)
        db.session.commit()
 
        client.close()
 
        # Save test questions in the ProfTestQuestions table
        for question in test_questions:
            new_question = ProfTestQuestions(prof_test_id=new_test.id, question=question, correct_answer="")
            app.logger.info("question:", question)
 
            db.session.add(new_question)
 
        app.logger.info(completion.choices[0].message.content)
 
        db.session.commit()
 
        return jsonify({"message": f"Profession added successfully, and a test has been created. {completion.choices[0].message.content}"})
 
    return result[0]  # Return the entire response, including errors


@app.route("/delete_prof/<prof_id>", methods=["DELETE"])
def delete_prof(prof_id):
    return handle_delete(Profession, prof_id)

@app.route("/update_prof/<prof_id>", methods=["PUT"])
def update_prof(prof_id):
    return handle_update(Profession, prof_id)

if __name__ == "__main__":
    app.run(debug=True)