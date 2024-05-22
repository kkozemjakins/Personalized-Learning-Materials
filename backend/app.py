#app.py
from flask import Flask, request, jsonify, session, Response, current_app, send_file, redirect, url_for
from firestore import initialize_firestore
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime, timedelta
import requests
import os
import openai
import json
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import glob
import firebase_admin
from firebase_admin import credentials, auth, firestore
import pyrebase


from GUD import get_entities,get_entity_by_id,add_entity,delete_entity,update_entity

from keys import CLIENT_ID, CLIENT_SECRET, GOOGLE_REDIRECT_URI,FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FIREBASE_CONFIG, OPENAI_API_KEY

app = Flask(__name__)

# Initialize Firestore

db = initialize_firestore()

firebase_py = pyrebase.initialize_app(FIREBASE_CONFIG)
authPY = firebase_py.auth()
dbPY = firebase_py.database()


# CORS setup
CORS(app)

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Google
GOOGLE_CLIENT_ID = CLIENT_ID
GOOGLE_CLIENT_SECRET = CLIENT_SECRET
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Firebase
firebase_cred = credentials.Certificate("secret/eduaisystem-firebase-adminsdk-f8s0n-187930ae20.json")
firebase_admin.initialize_app(firebase_cred, name="myapp")
firestore_db = firestore.client()


openai.api_key = OPENAI_API_KEY

def get_openai_response_json(system_request, prompt):
    try:
        # Debug: Print system request and prompt
        print("System Request:", system_request)
        print("Prompt:", prompt)

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            top_p=0.9,
            response_format= {"type": "json_object"},
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": prompt}
            ]
        )

        # Debug: Print raw response from OpenAI API
        print("Raw Response:", response)

        # Extract the response content
        response_content = response['choices'][0]['message']['content']
        
        # Debug: Print response content
        print("Response Content:", response_content)

        # Parse the response content as JSON
        json_content = json.loads(response_content)
        
        return json_content

    except openai.error.OpenAIError as e:
        # Handle specific OpenAI API errors
        print(f"OpenAI API error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"JSON decoding error occurred: {e}")
        print("Response Content:", response_content)
        return None
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred: {e}")
        return None


def get_openai_response(system_request, prompt,max_tokens):
    
    try:
        # Call the OpenAI API
        client = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response content
        response = client['choices'][0]['message']['content']
        
        
        return response
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/google/signup")
def google_signup():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/google/signup/callback")
def google_signup_callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_data = userinfo_response.json()

    # Create or get user
    user = authPY.get_user_by_email(userinfo_data["email"])

    if not user:
        # Create user
        user = authPY.create_user(
            email=userinfo_data["email"],
            email_verified=userinfo_data["email_verified"],
            password="default_password",
            display_name=userinfo_data.get("name", ""),
            photo_url=userinfo_data.get("picture", "")
        )

    # Create custom token
    custom_token = authPY.create_custom_token(user.uid)

    return jsonify({"token": custom_token.decode()})
# Facebook sign up
FACEBOOK_APP_ID = FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = FACEBOOK_APP_SECRET
FACEBOOK_REDIRECT_URI = "https://yourdomain.com/facebook/signup/callback"

@app.route("/facebook/signup")
def facebook_signup():
    return redirect(f"https://www.facebook.com/v11.0/dialog/oauth?client_id={FACEBOOK_APP_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&scope=email")

@app.route("/facebook/signup/callback")
def facebook_signup_callback():
    code = request.args.get("code")

    access_token_url = f"https://graph.facebook.com/v11.0/oauth/access_token?client_id={FACEBOOK_APP_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&client_secret={FACEBOOK_APP_SECRET}&code={code}"
    access_token_response = requests.get(access_token_url)
    access_token_data = access_token_response.json()
    access_token = access_token_data["access_token"]

    # Get user info
    user_info_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
    user_info_response = requests.get(user_info_url)
    user_info = user_info_response.json()

    # Here, you can use user_info['email'] and user_info['name'] to register the user

    return jsonify(user_info)


@app.route("/signup", methods=["POST"])
def signup_user():
    email = request.json["email"]
    password = request.json["password"]
    username = request.json["username"]

    try:
        user = authPY.create_user_with_email_and_password(email, password)
        
        user_data = {
            "email": email,
            "username": username,
            "role": "user",
        }
        
        add_entity(db.collection('users'), user_data)

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/login", methods=["POST"])
def login_user():
    email = request.json['email']
    password = request.json['password']
    
    try:
        user = authPY.sign_in_with_email_and_password(email, password)
        user_data = authPY.get_account_info(user['idToken'])
        
        # Check if the user is an admin
        admin_check = db.collection('admins').where("email", "==", email).stream()
        is_admin = False
        for admin in admin_check:
            is_admin = True
            break

        # Get user ID
        user_id = user_data['users'][0]['localId']

        # Check if the user is an admin
        if is_admin:
            return jsonify({**user_data, "user_id": user_id, "is_admin": True}), 200
        else:
            return jsonify({**user_data, "user_id": user_id, "is_admin": False}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    

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








@app.route("/get_test/<test_id>", methods=["GET"])
def get_test_by_id(test_id):
    return get_entity_by_id(db.collection('Tests'), "test", ["profession_id", "question_amount"], test_id)

@app.route("/get_tests", methods=["GET"])
def get_tests():
    return get_entities(db.collection('Tests'), "Tests", ["profession_id", "question_amount"])

@app.route("/add_test", methods=["POST"])
def add_test():
    data = {
        "profession_id": request.json["profession_id"],
        "question_amount": request.json["question_amount"]
    }
    return add_entity(db.collection('Tests'), data)

@app.route("/delete_test/<test_id>", methods=["DELETE"])
def delete_test(test_id):
    return delete_entity(db.collection('Tests'), test_id)

@app.route("/update_test/<test_id>", methods=["PUT"])
def update_test(test_id):
    data = {
        "profession_id": request.json.get("profession_id"),
        "question_amount": request.json.get("question_amount")
    }
    return update_entity(db.collection('Tests'), test_id, data)

@app.route("/get_test_questions_by_profession/<profession_id>", methods=["GET"])
def get_test_questions_by_profession(profession_id):
    try:
        profession = db.collection('professions').document(profession_id).get()
        if not profession.exists:
            return jsonify({'error': 'Profession not found'}), 404

        prof_tests = db.collection('Tests').where("profession_id", "==", profession_id).stream()
        test_questions = []
        for prof_test in prof_tests:
            questions = db.collection('TestQuestions').where("prof_test_id", "==", prof_test.id).stream()
            for question in questions:
                test_questions.append({
                    'question_id': question.id,
                    'prof_test_id': question.get("prof_test_id"),
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


@app.route("/get_test_questions", methods=["GET"])
def get_tests_questions():
    return get_entities(db.collection('TestQuestions'), "profTestCreatedQuestions", ["id", "prof_test_id", "level_of_question", "question", "correct_answer", "answer_variant1", "answer_variant2", "answer_variant3", "answer_variant4"])


@app.route("/add_test_questions", methods=["POST"])
def add_test_questions():
    data = {
        "prof_test_id": request.json["prof_test_id"],
        "question": request.json["question"],
        "correct_answer": request.json["correct_answer"],
        "level_of_question": request.json["level_of_question"],
        "answer_variant1": request.json["answer_variant1"],
        "answer_variant2": request.json["answer_variant2"],
        "answer_variant3": request.json["answer_variant3"],
        "answer_variant4": request.json["answer_variant4"]
    }
    return add_entity(db.collection('TestQuestions'), data)

@app.route("/delete_test_questions/<test_questions_id>", methods=["DELETE"])
def delete_test_questions(test_questions_id):
    return delete_entity(db.collection('TestQuestions'), test_questions_id)

@app.route("/update_test_questions/<test_questions_id>", methods=["PUT"])
def update_test_questions(test_questions_id):
    data = {
        "prof_test_id": request.json.get("prof_test_id"),
        "question": request.json.get("question"),
        "correct_answer": request.json.get("correct_answer"),
        "level_of_question": request.json.get("level_of_question"),
        "answer_variant1": request.json.get("answer_variant1"),
        "answer_variant2": request.json.get("answer_variant2"),
        "answer_variant3": request.json.get("answer_variant3"),
        "answer_variant4": request.json.get("answer_variant4")
    }
    return update_entity(db.collection('TestQuestions'), test_questions_id, data)

# Profession adding/viewing/modifying/deleting
@app.route("/get_prof", methods=["GET"])
def get_prof():
    return get_entities(db.collection('professions'), "professions", ["id", "profession_name", "profession_description"])


@app.route("/get_prof/<prof_id>", methods=["GET"])
def get_prof_by_id(prof_id):
    return get_entity_by_id(db.collection('professions'), "professions", ["profession_name", "profession_description"], prof_id)

@app.route("/add_prof", methods=["POST"])
def add_prof():
    dataT = {
        "profession_name": request.json.get("profession_name"),
        "profession_description": request.json.get("profession_description")
    }
    result = db.collection('professions').add(dataT)

    print(f"prof id data:", result[1].id)


    # Check if the profession was added successfully
    if result[1].id:
        # Profession added successfully, now create a test using OpenAI
        profession_name = request.json.get("profession_name")
        profession_description = request.json.get("profession_description")
        

        # Customize the OpenAI chat completions creation based on your requirements
        system_request = "You will be provided with a profession and its description, and on this basis, you will need to create a test that will test knowledge level of junior specialist about the profession main skills, with 30 questions of different levels and answers to them. 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions, in total need to be 30 questions related to lastest skills needed in that junior  specialist role."
        user_request = f"Generate 15 basic level questions, 10 intermediate level questions, and 5 advanced level questions with answers for the newly added profession - {profession_name}, profession description - {profession_description}. The design should be like this - question number, question, question level in brackets and a list of 4 answer options. And can you output it with JSON array. For each question the question level will have to be written. Also please don't use newline characters and the leading and trailing backticks from the string. Please use this example of output as a template: " + \
        """
        {
            "questions": [{
                "question_number": 1,
                "question": "What is the main area of expertise for a Full Stack Developer as described in the profession description?",
                "question_level": "basic",
                "answers": ["Mobile Development", "JVM related technologies", "Data Analysis"], 
                "correct_answer": "Cybersecurity"
            }]
        }
        """


        client = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": user_request}
            ]
        )


        # Extract test details from OpenAI response
        # Assuming that the response contains a 'choices' field
        test_content = get_openai_response(system_request,user_request)

        

        print(f"GPT data:", test_content)

        try:
            test_questions_data = json.loads(test_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": test_content}), 500

        profession_id = result[1].id

        # Create a new profession test
        new_test = db.collection('Tests').document()
        new_test.set({
            "profession_id": profession_id,
            "question_amount": len(test_questions_data["questions"])
        })

        # Add test questions to the database
        for question_data in test_questions_data["questions"]:
            new_question = db.collection('TestQuestions').document()
            new_question.set({
                "prof_test_id": new_test.id,
                "question": question_data["question"],
                "level_of_question": question_data["question_level"],
                "correct_answer": question_data["correct_answer"],
                "answer_variant1": question_data["answers"][0],
                "answer_variant2": question_data["answers"][1],
                "answer_variant3": question_data["answers"][2],
                "answer_variant4": question_data["answers"][3]
            })

        return jsonify({"message": f"Profession added successfully, and a test has been created with questions.", "profession_id": profession_id})

    return result  # Return the entire response, including errors


@app.route("/delete_prof/<prof_id>", methods=["DELETE"])
def delete_prof(prof_id):
    return delete_entity(db.collection('professions'), prof_id)

@app.route("/update_prof/<prof_id>", methods=["PUT"])
def update_prof(prof_id):
    return update_entity(db.collection('professions'), prof_id)


@app.route("/submit_test_results", methods=["POST"])
def submit_test_results():
    data = request.json
    profession_id = data.get("profession_id")
    user_id = data.get("user_id")
    mark = data.get("mark")
    correct_answers_amount = data.get("correct_answers_amount")
    incorrect_answers_amount = data.get("incorrect_answers_amount")

    # Fetch profession information
    profession = db.collection('professions').document(profession_id).get()
    if not profession.exists:
        return jsonify({"error": "Profession not found"}), 404

    profession_info = profession.to_dict()
    profession_name = profession_info["profession_name"]
    profession_description = profession_info["profession_description"]

    # Fetch profession test information based on profession_id
    prof_tests = db.collection('Tests').where("profession_id", "==", profession_id).stream()
    prof_test_id = None
    for prof_test in prof_tests:
        prof_test_id = prof_test.id

    if not prof_test_id:
        return jsonify({"error": "Profession test not found for the given profession"}), 404

    # Fetch user answers for the test
    user_answers_ref = db.collection('ProfTestUserResults').where("prof_test_id", "==", prof_test_id).where("user_id", "==", user_id)
    user_answers = user_answers_ref.stream()
    user_answers_data = [{"question_id": ans.id, "user_answer": ans.to_dict()["user_answer"], "correct_incorrect": ans.to_dict()["correct_incorrect"]} for ans in user_answers]

    # Prepare request prompt for OpenAI based on user answers
    prompt = ""
    for ans_data in user_answers_data:
        question = db.collection('TestQuestions').document(ans_data["question_id"]).get().to_dict()
        prompt += f"user answered {ans_data['user_answer']} on question - {question['question']} Level: {question['level_of_question']}, but correct answer was {question['correct_answer']}. "

    system_request = f"You will be provided with answers to the test for the profession {profession_name} - {profession_description}. Your task is to analyze the user`s answers and create , based on results, an course outline for a training course for junior specialists, covering all the topics necessary for starting in this profession. Here is example of module progression, please follow it while creating response - Module 1: Introduction to JavaScript, Module 2: Core JavaScript Concepts, Module 3: Intermediate JavaScript, Module 4: Advanced JavaScript, Module 5: Front-End Frameworks and Libraries, Module 6: Back-End JavaScript, Module 7: Testing and Deployment, Module 8: Advanced Topics, Module 9: Project Development.Each outline should include a theory section and at least two practical tasks for each topic, along with recommendations and resources for further study, preferably including YouTube links and other recommended materials related to each specific topic. This information should be generated in JSON format, strictly based ONLY on the following template, use all available tokens to generate response." + \
    """
    
{
  "course_outline": {
    "title": "JavaScript Developer from Beginner to Advanced",
    "modules": [
      {
        "title": "Introduction to JavaScript",
        "order": 1,
        "sections": [
          {
            "title": "Basic Syntax",
            "topics": [
              {
                "title": "Variables and Data Types",
                "theory": "Introduction to variables and data types.",
                "tasks": [],
                "recommendations": ["useful links", "videos"]
              }
            ]
          }
        ]
      }
    ]
  }
}


"""

    
    response = get_openai_response_json(system_request, prompt)
        
    if response is None:
        return jsonify({"error": "Failed to generate response from OpenAI"}), 500

    json_content = response

    print("JSON:", json_content)

    # Save data to the database
    # Save to UserCourses table
    user_course_ref = db.collection('UserCourses').document()
    user_course_ref.set({
        "userID": user_id,
        "professionID": profession_id
    })
    user_course_id = user_course_ref.id

    modules = json_content['course_outline']['modules']

    print(f"Number of modules: {len(modules)}")

    for module in modules:
        module_title = module['title']
        module_order = module['order']
        course_module_ref = db.collection('CourseModules').document()
        course_module_id = course_module_ref.id  # Capture the module ID

        course_module_ref.set({
            "UserCourseID": user_course_id,
            "ModuleTitle": module_title,
            "ModuleOrder": module_order,
        })

        sections = module.get('sections', [])

        for section in sections:
            section_title = section['title']
            course_section_ref = db.collection('CourseSections').document()
            course_section_id = course_section_ref.id  # Capture the section ID

            course_section_ref.set({
                "ModuleID": course_module_id,
                "SectionTitle": section_title,
            })

            topics = section.get('topics', [])

            for topic in topics:
                topic_title = topic['title']
                theory_content = topic['theory']
                recommendations = topic.get('recommedations', [])
                tasks = topic.get('tasks', [])

                course_topic_ref = db.collection('CourseTopics').document()
                course_topic_id = course_topic_ref.id  # Capture the topic ID

                course_topic_ref.set({
                    "SectionID": course_section_id,
                    "TopicTitle": topic_title,
                })

                theory_ref = db.collection('CourseTopicsTheory').document()
                topic_theory_id = theory_ref.id  # Capture the theory ID

                theory_ref.set({
                    "TopicID": course_topic_id,
                    "TheoryContent": theory_content
                })

                for rec in recommendations:
                    links_ref = db.collection('TopicsTheoryRecommendations').document()
                    links_ref.set({
                        "TheoryID": topic_theory_id,
                        "Source": rec
                    })

                for task in tasks:
                    tasks_ref = db.collection('TopicsTheoryTasks').document()
                    tasks_ref.set({
                        "TheoryID": topic_theory_id,
                        "PracticalTask": task
                    })

    print("Data saved successfully.")


    # Save to ProfTestMarks table
    new_test_result = db.collection('ProfTestMarks').document()
    new_test_result.set({
        "prof_test_id": prof_test_id,
        "user_id": user_id,
        "mark": mark,
        "correct_answers_amount": correct_answers_amount,
        "incorrect_answers_amount": incorrect_answers_amount,
    })

    result_id = new_test_result.id  # Get the ID of the newly created test result

    return jsonify({"user_marks_id": result_id})  # Return user_marks_id


@app.route("/get_course/<course_id>", methods=["GET"])
def get_course(course_id):
    course_ref = db.collection('UserCourses').document(course_id)
    course_data = course_ref.get().to_dict()

    if not course_data:
        return jsonify({"error": "Course not found"}), 404

    profession_ref = db.collection('professions').document(course_data["professionID"])
    profession_info = profession_ref.get().to_dict()
    modules_data = []
    modules_ref = db.collection('CourseModules').where("UserCourseID", "==", course_id).stream()
    for module in modules_ref:
        module_data = module.to_dict()
        module_id = module.id

        sections_data = []
        sections_ref = db.collection('CourseSections').where("ModuleID", "==", module_id).stream()
        for section in sections_ref:
            section_data = section.to_dict()
            section_id = section.id

            topics_data = []
            topics_ref = db.collection('CourseTopics').where("SectionID", "==", section_id).stream()
            for topic in topics_ref:
                topic_data = topic.to_dict()
                topic_id = topic.id

                theory_docs = db.collection('CourseTopicsTheory').where("TopicID", "==", topic_id).stream()
                theory_data = [doc.to_dict() for doc in theory_docs]

                recommendations_ref = db.collection('TopicsTheoryRecommendations').where("TheoryID", "==", topic_id).stream()
                recommendations_data = [rec.to_dict() for rec in recommendations_ref]

                tasks_ref = db.collection('TopicsTheoryTasks').where("TheoryID", "==", topic_id).stream()
                tasks_data = [task.to_dict() for task in tasks_ref]

                topic_data["theory"] = theory_data
                topic_data["recommendations"] = recommendations_data
                topic_data["tasks"] = tasks_data
                topics_data.append(topic_data)

            section_data["topics"] = topics_data
            sections_data.append(section_data)

        module_data["sections"] = sections_data
        modules_data.append(module_data)

    test_results_ref = db.collection('ProfTestMarks').where("prof_test_id", "==", course_id).stream()
    test_results_data = [doc.to_dict() for doc in test_results_ref]

    course_info = {
        "id": course_id,
        "profession": profession_info,
        "modules": sorted(modules_data, key=lambda x: x["ModuleOrder"]),  # Sort modules by order
        "test_results": test_results_data
    }

    return jsonify(course_info), 200



@app.route("/get_user_course/<user_id>", methods=["GET"])
def get_user_courses(user_id):
    user_courses = db.collection('UserCourses').where("userID", "==", user_id).stream()
    courses_data = []

    for user_course in user_courses:
        course_data = user_course.to_dict()
        profession = db.collection('professions').document(course_data["professionID"]).get()
        profession_info = profession.to_dict() if profession.exists else {}

        modules_data = []
        modules = db.collection('CourseModules').where("UserCourseID", "==", user_course.id).stream()
        for module in modules:
            module_data = module.to_dict()
            module_id = module.id

            sections_data = []
            sections = db.collection('CourseSections').where("ModuleID", "==", module_id).stream()
            for section in sections:
                section_data = section.to_dict()
                section_id = section.id

                topics_data = []
                topics = db.collection('CourseTopics').where("SectionID", "==", section_id).stream()
                for topic in topics:
                    topic_data = topic.to_dict()
                    topic_id = topic.id

                    theory_docs = db.collection('CourseTopicsTheory').where("TopicID", "==", topic_id).stream()
                    theory_data = [doc.to_dict() for doc in theory_docs]

                    recommendations = db.collection('TopicsTheoryRecommendations').where("TheoryID", "==", topic_id).stream()
                    recommendations_data = [rec.to_dict() for rec in recommendations]

                    tasks = db.collection('TopicsTheoryTasks').where("TheoryID", "==", topic_id).stream()
                    tasks_data = [task.to_dict() for task in tasks]

                    topic_data["theory"] = theory_data
                    topic_data["recommendations"] = recommendations_data
                    topic_data["tasks"] = tasks_data
                    topics_data.append(topic_data)

                section_data["topics"] = topics_data
                sections_data.append(section_data)

            module_data["sections"] = sections_data
            modules_data.append(module_data)

        test_results_docs = db.collection('ProfTestMarks').where("prof_test_id", "==", user_course.id).where("user_id", "==", user_id).stream()
        test_results_data = [doc.to_dict() for doc in test_results_docs]

        course_info = {
            "id": user_course.id,
            "profession": profession_info,
            "modules": sorted(modules_data, key=lambda x: x["ModuleOrder"]),  # Sort modules by order
            "test_results": test_results_data
        }

        courses_data.append(course_info)

    return jsonify(courses_data), 200



@app.route("/get_course_modules/<course_id>", methods=["GET"])
def get_course_modules(course_id):
    course_modules = db.collection('CourseModules').where("UserCourseID", "==", course_id).stream()
    modules_data = []

    for module in course_modules:
        module_data = module.to_dict()
        module_id = module.id

        sections_data = []
        sections = db.collection('CourseSections').where("ModuleID", "==", module_id).stream()
        for section in sections:
            section_data = section.to_dict()
            section_id = section.id
            sections_data.append({"id": section_id, "title": section_data["SectionTitle"]})

        module_info = {"id": module_id, "title": module_data["ModuleTitle"], "sections": sections_data}
        modules_data.append(module_info)

    return jsonify(modules_data), 200

@app.route("/get_section_topics/<course_id>/<module_id>/<section_id>", methods=["GET"])
def get_section_topics(course_id, module_id, section_id):
    topics = db.collection('CourseTopics').where("SectionID", "==", section_id).stream()
    topics_data = []

    for topic in topics:
        topic_data = topic.to_dict()
        topic_id = topic.id

        theory_docs = db.collection('CourseTopicsTheory').where("TopicID", "==", topic_id).stream()
        
        theory_data = []
        theory_ids = []
        
        # Collect theory data and IDs
        for theory_doc in theory_docs:
            theory_dict = theory_doc.to_dict()
            theory_dict['id'] = theory_doc.id
            theory_data.append(theory_dict)
            theory_ids.append(theory_doc.id)

        tasks_data = []

        # Fetch tasks for each theory document
        for theory_id in theory_ids:
            tasks = db.collection('TopicsTheoryTasks').where("TheoryID", "==", theory_id).stream()
            tasks_data.extend([task.to_dict() for task in tasks])

        topic_info = {
            "id": topic_id,
            "TopicTitle": topic_data["TopicTitle"],
            "theory": theory_data,
            "tasks": tasks_data
        }
        topics_data.append(topic_info)

    return jsonify({"topics": topics_data}), 200






@app.route("/save_user_answers", methods=["POST"])
def save_user_answers():
    data = request.json

    # Save user answers to the database
    for answer_data in data:
        question_id = answer_data.get("questions_id")
        user_answer = answer_data.get("user_answer")
        
        # Fetch the correct answer for the question
        question = db.collection('TestQuestions').document(question_id).get().to_dict()
        correct_answer = question["correct_answer"]
        
        # Determine if the user's answer is correct
        correct_incorrect = 1 if user_answer == correct_answer else 0

        # Save user answer and correctness to the database
        new_user_answer = db.collection('ProfTestUserResults').document()
        new_user_answer.set({
            "user_id": answer_data.get("user_id"),
            "user_marks_id": answer_data.get("user_marks_id"),
            "questions_id": question_id,
            "user_answer": user_answer,
            "correct_incorrect": correct_incorrect
        })

    return jsonify({"message": "User answers saved successfully"})

@app.route("/user_answers/<user_id>", methods=["GET"])
def get_user_answers(user_id):
    user_answers_ref = db.collection('ProfTestUserResults').where("user_id", "==", user_id)
    user_answers = user_answers_ref.stream()

    user_answers_data = []
    for answer in user_answers:
        question = db.collection('TestQuestions').document(answer.to_dict()["questions_id"]).get().to_dict()
        prof_test = db.collection('Tests').document(question["prof_test_id"]).get().to_dict()
        profession = db.collection('professions').document(prof_test["profession_id"]).get().to_dict()

        # Fetching additional information from ProfTestMarks
        prof_test_marks_id = answer.to_dict()["user_marks_id"]
        prof_test_marks = db.collection('ProfTestMarks').document(prof_test_marks_id).get().to_dict()

        user_answer_info = {
            "id": answer.id,
            "prof_test_id": question["prof_test_id"],
            "questions_id": answer.to_dict()["questions_id"],
            "user_answer": answer.to_dict()["user_answer"],
            "correct_incorrect": answer.to_dict()["correct_incorrect"],
            "question_text": question["question"],
            "question_level": question["level_of_question"],
            "prof_test_results_marks_id": answer.to_dict()["user_marks_id"],
            "profession_name": profession["profession_name"],
            "profession_description": profession["profession_description"],
            "correct_answer": question["correct_answer"],
            "mark": prof_test_marks["mark"]
        }

        user_answers_data.append(user_answer_info)

    return jsonify({"userAnswers": user_answers_data}), 200




@app.route("/delete_all_test_results", methods=["DELETE"])
def delete_all_test_results():
    try:
        # Delete all data from ProfTestMarks and ProfTestUserResults tables
        db.collection('ProfTestMarks').stream()
        db.collection('ProfTestUserResults').stream()
        return jsonify({"message": "All test results deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to delete test results: {str(e)}"}), 500




#Courses
# Courses


@app.route("/get_theory/<theory_id>", methods=["GET"])
def get_theory(theory_id):
    try:
        # Fetch theory data from your database based on the provided theory_id
        theory_ref = db.collection('CourseTopicsTheory').where("CourseTopicID", "==", theory_id).limit(1)
        theory_doc = theory_ref.get()

        if not theory_doc:
            return jsonify({"error": "Theory not found"}), 404
        
        theory_data = theory_doc[0].to_dict()

        # Fetch topic data based on the CourseTopicID
        topic_ref = db.collection('CourseTopics').document(theory_data["CourseTopicID"])
        topic_doc = topic_ref.get()
        if not topic_doc.exists:
            return jsonify({"error": "Topic not found"}), 404
        
        topic_data = topic_doc.to_dict()

        # Fetch links related to the theory
        links_ref = db.collection('CourseTopicsRecLinks').where("TopicsTheoryID", "==", theory_id).stream()
        links_data = [link.to_dict()["SourceLink"] for link in links_ref]

        # Fetch tasks related to the topic
        tasks_ref = db.collection('CourseTopicsTasks').where("CourseTopicID", "==", theory_data["CourseTopicID"]).stream()
        task_ids = [task.id for task in tasks_ref]


        # Construct the theory information object
        theory_info = {
            "title": topic_data.get("TopicTitle", "Untitled Topic"),  
            "description": theory_data.get("TheoryContent", "No description available"),  
            "links": links_data,
            "task_ids": task_ids
        }
        
        return jsonify(theory_info), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_task/<task_id>", methods=["GET"])
def get_task(task_id):
    try:
        # Fetch task data from your database based on the provided task_id
        task_ref = db.collection('CourseTopicsTasks').document(task_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            return jsonify({"error": "Task not found"}), 404
        
        task_data = task_doc.to_dict()

        # Construct the task information object
        task_info = {
            "description": task_data.get("PracticalTask", "No description available"),  
            # Add more task details here
        }
        
        return jsonify(task_info), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/submit_answer/<task_id>", methods=["POST"])
def submit_answer(task_id):
    try:
        # Parse the request JSON data
        data = request.json
        user_id = data.get("userId")
        answer = data.get("answer")

        # Save the answer to the UserAnswerTask table in Firestore
        db.collection("UserAnswerTask").add({
            "userId": user_id,
            "taskId": task_id,
            "answer": answer
        })

        return jsonify({"message": "Answer submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)