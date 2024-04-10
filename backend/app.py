#app.py
from flask import Flask, request, jsonify, session, Response, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User, Profession, ProfTest, ProfTestQuestions, ProfTestMarks, ProfTestUserResults
import openai
import json
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
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
        # Add more user information here as needed
    })


######
def get_entities(model, entity_name, fields):
    entities = model.query.all()
    entity_list = [{field: getattr(entity, field) for field in fields} for entity in entities]
    print(f"{entity_name} data:", entity_list)
    return jsonify({entity_name: entity_list})

def get_entity_by_id(model, entity_name, fields, entity_id):
    entity = model.query.get(entity_id)
    if entity:
        entity_data = {field: getattr(entity, field) for field in fields}
        print(f"{entity_name} data:", entity_data)
        return jsonify({entity_name: entity_data})
    else:
        return jsonify({"error": f"{entity_name} not found"}), 404


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

@app.route("/get_user/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    return get_entity_by_id(User, "profession", ["id", "email", "role_id"], user_id)


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

@app.route('/get_test_questions_by_profession/<profession_id>', methods=['GET'])
def get_test_questions_by_profession(profession_id):
    try:
        profession = Profession.query.get(profession_id)
        if not profession:
            return jsonify({'error': 'Profession not found'}), 404

        prof_tests = ProfTest.query.filter_by(profession_id=profession_id).all()
        test_questions = []
        for prof_test in prof_tests:
            questions = ProfTestQuestions.query.filter_by(prof_test_id=prof_test.id).all()
            for question in questions:
                test_questions.append({
                    'question_id': question.id,
                    'question': question.question,
                    'level_of_question': question.level_of_question,
                    'correct_answer': question.correct_answer,
                    'answer_variant1': question.answer_variant1,
                    'answer_variant2': question.answer_variant2,
                    'answer_variant3': question.answer_variant3,
                    'answer_variant4': question.answer_variant4
                })

        return jsonify(test_questions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

@app.route("/get_prof/<prof_id>", methods=["GET"])
def get_prof_by_id(prof_id):
    return get_entity_by_id(Profession, "profession", ["id", "profession_name", "profession_description"], prof_id)

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

@app.route("/submit_test_results", methods=["POST"])
def submit_test_results():
    data = request.json
    profession_id = data.get("profession_id")
    user_id = data.get("user_id")
    mark = data.get("mark")
    correct_answers_amount = data.get("correct_answers_amount")
    incorrect_answers_amount = data.get("incorrect_answers_amount")

    # Fetch profession information
    profession_info = Profession.query.get(profession_id)
    if not profession_info:
        return jsonify({"error": "Profession not found"}), 404

    # Fetch profession test information based on profession_id
    prof_test_info = ProfTest.query.filter_by(profession_id=profession_id).first()
    if not prof_test_info:
        return jsonify({"error": "Profession test not found for the given profession"}), 404

    # Extract prof_test_id from the prof_test_info
    prof_test_id = prof_test_info.id

    profession = profession_info.profession_name
    profession_description = profession_info.profession_description

    # Fetch user answers for the test
    user_answers = ProfTestUserResults.query.filter_by(prof_test_id=prof_test_id, user_id=user_id).all()
    user_answers_data = [{"question_id": ans.questions_id, "user_answer": ans.user_answer, "correct_incorrect": ans.correct_incorrect} for ans in user_answers]

    # Prepare request prompt for OpenAI based on user answers
    prompt = ""
    for ans_data in user_answers_data:
        prompt += f"user answered {ans_data['user_answer']} on question - {ProfTestQuestions.query.get(ans_data['question_id']).question} Level: {ProfTestQuestions.query.get(ans_data['question_id']).level_of_question}, but correct answer was {ProfTestQuestions.query.get(ans_data['question_id']).correct_answer}. "

    system_request = f"You will be provided with answers to the test for the profession {profession} - {profession_description}. Your task is to analyze the user`s answers and provide general comments on test results and based on that result create an outline for a training course for junior specialists, covering all the topics necessary for starting in this profession. Each outline should include a theory section and at least two practical tasks for each topic, along with recommendations and resources for further study, preferably including YouTube links and other recommended materials related to each specific topic. This information should be generated in XML format, based ONLY on the following template." + \
    """<course_outline>
      <profession_description>
        <!-- Replace 'Profession Name' with the actual name of the profession -->
        <name>Profession Name</name>
        <!-- Replace 'A brief description of the profession and its significance' with the actual description -->
        <description>A brief description of the profession and its significance.</description>
      </profession_description>
      <topics>
        <topic>
          <title>Topic Title 1</title>
          <theory_section>
            <description>Description of the theory behind Topic 1.</description>
            <recommendations>
              <recommendation>Book/Article name for further reading.</recommendation>
              <recommendation>YouTube link for related video.</recommendation>
            </recommendations>
          </theory_section>
          <practical_tasks>
            <task>Description of Practical Task 1 related to Topic 1.</task>
            <task>Description of Practical Task 2 related to Topic 1.</task>
          </practical_tasks>
        </topic>
        <topic>
          <title>Topic Title 2</title>
          <theory_section>
            <description>Description of the theory behind Topic 2.</description>
            <recommendations>
              <recommendation>Book/Article name for further reading.</recommendation>
              <recommendation>YouTube link for related video.</recommendation>
            </recommendations>
          </theory_section>
          <practical_tasks>
            <task>Description of Practical Task 1 related to Topic 2.</task>
            <task>Description of Practical Task 2 related to Topic 2.</task>
          </practical_tasks>
        </topic>
        <!-- Add more topics as needed following the same structure -->
      </topics>
      <general_comments>
        <comment>The user has a strong foundation in Java development and related technologies but may benefit from further experience with containerization tools, cloud development, and additional programming languages.</comment>
        <improvement_recommendations>It is recommended to explore containerization tools like Docker and Kubernetes, gain experience with cloud platforms such as AWS or Azure, and expand knowledge by learning new programming languages like GoLang and TypeScript.</improvement_recommendations>
      </general_comments>
    </course_outline>"""

    
    client = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_request},
            {"role": "user", "content": prompt}
        ]
    )
    comment_on_results = client['choices'][0]['message']['content']
    
    # Save test results to the database
    new_test_result = ProfTestMarks(
        prof_test_id=prof_test_id,
        user_id=user_id,
        mark=mark,
        correct_answers_amount=correct_answers_amount,
        incorrect_answers_amount=incorrect_answers_amount,
        comment_on_results=comment_on_results
    )
    db.session.add(new_test_result)
    db.session.commit()

    # Create XML content
    xml_content = create_xml_content(comment_on_results)

    # Save XML content to a file
    user_id = data.get("user_id")
    result_id = new_test_result.id
    filename = f"user_{user_id}_result_{result_id}.xml"
    file_path = os.path.join(current_app.root_path, "xml_files", filename)
    with open(file_path, "w") as f:
        f.write(xml_content)

    return send_file(file_path, as_attachment=True)

def create_xml_content(comment_on_results):
    # Convert the comment_on_results directly to XML content
    xml_content = comment_on_results
    
    return xml_content

@app.route("/get_user_xml/<user_id>", methods=["GET"])
def get_user_xml(user_id):
    try:
        # Search for XML files based on user ID
        xml_files = glob.glob(os.path.join(current_app.root_path, "xml_files", f"user_{user_id}_result_*.xml"))
        if not xml_files:
            return jsonify({"error": "No XML files found for the specified user ID"}), 404
        
        # Read the content of all XML files
        xml_data = []
        for file_path in xml_files:
            with open(file_path, "r") as f:
                xml_content = f.read()
                xml_data.append(xml_content)

        return jsonify({"user_xmls": xml_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save_user_answers", methods=["POST"])
def save_user_answers():
    data = request.json

    # Save user answers to the database
    for answer_data in data:
        question_id = answer_data.get("questions_id")
        user_answer = answer_data.get("user_answer")
        
        # Fetch the correct answer for the question
        question = ProfTestQuestions.query.get(question_id)
        correct_answer = question.correct_answer
        
        # Determine if the user's answer is correct
        correct_incorrect = 1 if user_answer == correct_answer else 0

        # Save user answer and correctness to the database
        new_user_answer = ProfTestUserResults(
            prof_test_id=answer_data.get("prof_test_id"),
            user_id=answer_data.get("user_id"),
            user_marks_id=answer_data.get("user_marks_id"),
            questions_id=question_id,
            user_answer=user_answer,
            correct_incorrect=correct_incorrect
        )
        db.session.add(new_user_answer)

    db.session.commit()

    return jsonify({"message": "User answers saved successfully"})

@app.route("/user_answers/<user_id>", methods=["GET"])
def get_user_answers(user_id):
    # Query only from ProfTestUserResults table
    user_answers = ProfTestUserResults.query.filter_by(user_id=user_id).all()

    if user_answers:
        user_answers_data = []
        for answer in user_answers:
            # Fetch additional information from ProfTestMarks, ProfTestQuestions, and Profession
            question_info = ProfTestQuestions.query.get(answer.questions_id)
            prof_test_info = ProfTest.query.get(question_info.prof_test_id)
            mark_info = ProfTestMarks.query.get(prof_test_info.user_marks_ids)
            profession_info = Profession.query.get(prof_test_info.profession_id)
            
            user_answer_info = {
                "id": answer.id,
                "prof_test_id": question_info.prof_test_id,
                "questions_id": answer.questions_id,
                "user_answer": answer.user_answer,
                "correct_incorrect": answer.correct_incorrect,
                "question_text": question_info.question,
                "question_level": question_info.level_of_question,
                "prof_test_results_marks_id": mark_info.id,
                "comment_on_result": mark_info.comment_on_results,
                "profession_name": profession_info.profession_name,
                "profession_description": profession_info.profession_description
            }
            user_answers_data.append(user_answer_info)

        return jsonify({"userAnswers": user_answers_data}), 200
    else:
        return jsonify({"message": f"No user answers found for the specified user ID {user_id}"}), 404




@app.route("/delete_all_test_results", methods=["DELETE"])
def delete_all_test_results():
    try:
        # Delete all data from ProfTestMarks and ProfTestUserResults tables
        db.session.query(ProfTestMarks).delete()
        db.session.query(ProfTestUserResults).delete()
        db.session.commit()
        return jsonify({"message": "All test results deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete test results: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)