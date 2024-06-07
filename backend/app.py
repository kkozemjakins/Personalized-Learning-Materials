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

        model = 'gpt-4o'

        # Ensure the prompt or system request mentions 'json'
        if 'json' not in system_request.lower() and 'json' not in prompt.lower():
            raise ValueError("The system request or prompt must contain the word 'json'.")

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_request},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
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

def get_openai_response(system_request, prompt):
    
    try:
        # Call the OpenAI API
        client = openai.ChatCompletion.create(
            model="gpt-4o",
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
    professions = db.collection('professions').stream()
    response = []
    for prof in professions:
        data = prof.to_dict()
        data['id'] = prof.id  # Add the profession ID to the data dictionary
        sections = []
        for section_ref in prof.reference.collection('sections').stream():
            section_data = section_ref.to_dict()
            subsections = []
            for subsection_ref in section_ref.reference.collection('subsections').stream():
                subsection_data = subsection_ref.to_dict()
                subsections.append(subsection_data)
            section_data['subsections'] = subsections
            sections.append(section_data)
        data['sections'] = sections
        response.append(data)
    return jsonify({"professions": response})


@app.route("/get_prof/<prof_id>", methods=["GET"])
def get_prof_by_id(prof_id):
    prof_ref = db.collection('professions').document(prof_id)
    prof_data = prof_ref.get().to_dict()
    if not prof_data:
        return jsonify({"error": "Profession not found"}), 404
    
    sections = []
    for section_ref in prof_ref.collection('sections').stream():
        section_data = section_ref.to_dict()
        subsections = []
        for subsection_ref in section_ref.reference.collection('subsections').stream():
            subsection_data = subsection_ref.to_dict()
            subsections.append(subsection_data)
        section_data['subsections'] = subsections
        sections.append(section_data)
    prof_data['sections'] = sections
    
    return jsonify(prof_data)

@app.route("/add_prof", methods=["POST"])
def add_prof():

    profession_name = request.json.get("profession_name")
    print(profession_name)

    prompt_json = f"Generate a profession description for the {profession_name} using the following template:" + \
        """{
        "title": "Understanding the Role of a profession: Key Responsibilities, Workflow, and Career Path",
        "Introduction": {
            "Brief introduction": "Brief introduction to the role of a profession.",
            "Importance": "Explanation of why professionals in the profession field are crucial to their industry."
        },
        "main_body": {
            "section_1": {
                "Key Responsibilities": {
                    "Core duties": "Outline the primary duties that define the profession, highlighting any specific tasks they are responsible for.",
                    "Industry impact": "Discuss the impact that a profession has within their industry and how they contribute to business or organizational goals."
                }
            },
            "section_2": {
                "Typical workflow": {
                    "Step one": {
                        "Planning and preparation": "Describe the initial processes typically involved in the role of a profession, focusing on planning and strategizing.",
                        "Example": "Provide an example relevant to profession, such as planning a project or designing a strategy."
                    },
                    "Step two": {
                        "Execution": "Detail the execution phase, explaining how professionals in this role implement their plans.",
                        "Example": "Discuss specific tools or methodologies used in this profession."
                    },
                    "Step three": {
                        "Review and optimization": "Explain the review processes to ensure quality and effectiveness, including any follow-up actions.",
                        "Example": "Describe how a profession reviews outcomes and optimizes strategies for better results."
                    }
                }
            },
            "section_3": {
                "Learning path and career development": {
                    "Starting out": "Outline the basic skills and qualifications needed to enter this profession.",
                    "Learning resources": "Suggest foundational courses or training programs.",
                    "Developing expertise": "Discuss more advanced skills or specializations within the profession.",
                    "Practical exercise": "Recommend hands-on projects or challenges that help deepen expertise.",
                    "Advancing in the field": "Provide guidance on how to advance in the career, highlighting potential leadership or higher-level opportunities.",
                    "Professional growth": "Steps for gaining recognition and advancing within the field."
                }
            }
        }
    }
    """

    system_request_description = f"You would need to generate a profession description for the profession based on provided json template and profession"

    #test_content_prof = #get_openai_response_json(system_request_description,prompt_json)

    test_content_prof =  {
    "Title": "Understanding the Role of a Full Stack Developer: Key Responsibilities, Workflow, and Career Path",
    "Introduction": {
        "Brief introduction": "A Full Stack Developer is a versatile software engineer proficient in both front-end and back-end development. They have the ability to work on all layers of an application, from the user interface to the database and everything in between.",
        "Importance": "Full Stack Developers are crucial to the tech industry because they can handle multiple aspects of software development, ensuring that different parts of a project can work seamlessly together. Their broad skill set makes them invaluable in creating cohesive and fully-functional web applications."
    },
    "main_body": {
        "section_1": {
            "Key responsibilities": {
                "Core duties": "Full Stack Developers are responsible for designing and developing both client-side and server-side architecture. They write clean, functional code for both the front-end and back-end, build user interfaces, manage databases and servers, and ensure cross-platform optimization. Additionally, they often collaborate with other developers, designers, and stakeholders to bring projects to life.",      
                "Industry impact": "By bridging the gap between front-end and back-end development, Full Stack Developers streamline the development process and enhance the efficiency of software projects. Their ability to understand and implement both sides of an application allows for more cohesive and well-integrated products, ultimately contributing to the success and competitiveness of businesses in the tech industry."     
            }
        },
        "section_2": {
            "Typical workflow": {
                "Step one": {
                    "Planning and preparation": "Full Stack Developers begin with understanding project requirements and planning the architecture. This involves strategizing how to tackle both the front-end and back-end aspects, ensuring that all components will integrate smoothly.",   
                    "Example": "For instance, when developing a new web application, a Full Stack Developer might start by sketching wireframes and planning the database schema while considering the user experience and server-side logic."
                },
                "Step two": {
                    "Execution": "During execution, Full Stack Developers write code for both the client-side and server-side. They use various programming languages and frameworks to implement the planned architecture, such as HTML, CSS, and JavaScript for the front-end, and Node.js, Python, or Ruby for the back-end.",
                    "Example": "A Full Stack Developer might use React.js for building the user interface, while leveraging Express.js and MongoDB to handle server-side operations and database management."
                },
                "Step three": {
                    "Review and optimization": "After the initial development, Full Stack Developers review their code, test for bugs, and optimize performance. They may conduct code reviews, write unit tests, and implement feedback to ensure the application runs smoothly and efficiently.",
                    "Example": "A Full Stack Developer might use tools like Jest for testing, and engage in peer reviews to ensure code quality. They would then refine aspects like load time and responsiveness based on testing results."
                }
            }
        },
        "section_3": {
            "Learning path and career development": {
                "Starting out": "To become a Full Stack Developer, one typically needs a solid foundation in both front-end and back-end technologies. This includes proficiency in HTML, CSS, JavaScript, and at least one back-end language like Node.js or Python.",
                "Learning resources": "Foundational courses such as 'The Complete Web Developer Bootcamp' by Udemy or 'Full Stack Open' by the University of Helsinki are excellent starting points.",
                "Developing expertise": "As they progress, Full Stack Developers should learn more advanced frameworks and libraries, delve into database management, and explore cloud services. Specializing in areas like DevOps or mobile development can also be beneficial.",
                "Practical exercise": "Engaging in hands-on projects like building a complete web application from scratch, contributing to open-source projects, or participating in coding challenges can significantly deepen expertise.",
                "Advancing in the field": "To advance, Full Stack Developers can aim for roles such as Lead Developer, Solutions Architect, or even CTO. Gaining experience in project management and team leadership is crucial for these higher-level positions.",
                "Professional growth": "Continual learning through advanced courses, attending industry conferences, and obtaining certifications like AWS Certified Developer or Microsoft Azure Developer Associate can help Full Stack Developers gain recognition and advance within the field."
            }
        }
    }
}


    

    try:
    
        print("test_content_prof")
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": test_content_prof}), 500
    
    profession_description = test_content_prof.get("Introduction", {})
    

    dataT = {
        "profession_name": request.json.get("profession_name"),
        "profession_description": profession_description
    }
    result = db.collection('professions').add(dataT)

    print(f"prof id data:", result[1].id)


    main_body = test_content_prof.get("main_body", {})
    sections = []

    for section_key, section_value in main_body.items():
        for subsection_key, subsection_value in section_value.items():
            sections.append({
                "section_name": section_key,
                "subsection_name": subsection_key,
                "subsection_content": subsection_value
            })


    profession_ref = db.collection('professions').document(result[1].id)
    sections_ref = profession_ref.collection('sections')
    for section in sections:
        sections_ref.add(section)



    # Check if the profession was added successfully
    if result[1].id:
        # Profession added successfully, now create a test using OpenAI
        profession_name = request.json.get("profession_name")
        profession_description = test_content_prof
        

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



        # Extract test details from OpenAI response
        # Assuming that the response contains a 'choices' field

        test_content = get_openai_response_json(system_request,user_request)

        

        print(f"GPT data:", test_content)

        try:
            print(f"GPT data:", test_content)
            test_questions_data = test_content
            
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to parse test content JSON", "details": str(e), "content": test_content}), 500

        profession_id = result[1].id

        questions = test_questions_data.get("questions", [])
        if not questions:
            return jsonify({"error": "No questions found in the test content"}), 400

        # Use the question_number of the last question to determine the number of questions
        last_question_number = questions[-1].get("question_number")


        # Create a new profession test
        new_test = db.collection('Tests').document()
        new_test.set({
            "profession_id": profession_id,
            "question_amount": last_question_number
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

    return test_content_prof


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

    system_request = f"You will be provided with answers to the test for the profession {profession_name} - {profession_description}. Your task is to analyze the user`s answers and create , based on results, a really detailed course outline for a training course for junior specialists, covering all the topics necessary for starting in this profession. Here is example of module progression and structure, please follow it while creating response - Module 1: Introduction , Module 2: Core and Concepts, Module 3: Intermediate , Module 4: Advanced , Module 5: Moving towards more advance topics, Module 6: Continue to move towards advance topics, Module 7: Testing and Deployment, Module 8: Advanced Topics, Module 9: Project Development.Each outline should include a theory section and at least two practical tasks for each topic, along with recommendations and resources for further study, preferably including YouTube links and other recommended materials related to each specific topic. This information should be generated in JSON format, strictly based ONLY on the following template, use all available tokens to generate response." + \
    """
    
{
  "course_outline": {
    "title": "Course title",
    "modules": [
      {
        "title": "title of module",
        "order": 1,
        "sections": [
          {
            "title": "title of section",
            "order": 1,
            "topics": [
              {
                "title": "title of topic",
                "order": 1,
                "theory": "Theory part, that will explain topic",
                "tasks": [
                  {"order": 1, "task": "task content"},
                  {"order": 2, "task": "task content"}
                ],
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

    user_course_progress = {
        "UserID": user_id,
        "CourseID": user_course_id,
        "CourseCompletion": []
    }

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

        module_progress = {
            "ModuleID": course_module_id,
            "Completed": False,
            "ModuleOrder": module_order,
            "Sections": []
        }

        sections = module.get('sections', [])

        for section in sections:
            section_title = section['title']
            section_order = section['order']
            course_section_ref = db.collection('CourseSections').document()
            course_section_id = course_section_ref.id  # Capture the section ID

            course_section_ref.set({
                "ModuleID": course_module_id,
                "SectionTitle": section_title,
                "SectionOrder": section_order,
            })

            section_progress = {
                "SectionID": course_section_id,
                "Completed": False,
                "SectionOrder": section_order,
                "Topics": []
            }

            topics = section.get('topics', [])

            for topic in topics:
                topic_title = topic['title']
                topic_order = topic['order']
                theory_content = topic['theory']
                recommendations = topic.get('recommendations', [])
                tasks = topic.get('tasks', [])

                course_topic_ref = db.collection('CourseTopics').document()
                course_topic_id = course_topic_ref.id  # Capture the topic ID

                course_topic_ref.set({
                    "SectionID": course_section_id,
                    "TopicTitle": topic_title,
                    "TopicOrder": topic_order,
                })

                topic_progress = {
                    "TopicID": course_topic_id,
                    "Completed": False,
                    "TopicOrder": topic_order,
                    "TheoryID": None,
                    "Tasks": []
                }

                theory_ref = db.collection('CourseTopicsTheory').document()
                topic_theory_id = theory_ref.id  # Capture the theory ID

                theory_ref.set({
                    "TopicID": course_topic_id,
                    "TheoryContent": theory_content,
                    "TheoryOrder": 1
                })

                topic_progress["TheoryID"] = {
                    "TheoryID": topic_theory_id,
                    "Completed": False,
                    "TheoryOrder": 1
                }

                for task in tasks:
                    task_order = task['order']
                    task_content = task['task']
                    tasks_ref = db.collection('TopicsTheoryTasks').document()
                    task_id = tasks_ref.id  # Capture the task ID

                    tasks_ref.set({
                        "TheoryID": topic_theory_id,
                        "PracticalTask": task_content,
                        "TaskOrder": task_order
                    })

                    topic_progress["Tasks"].append({
                        "TaskID": task_id,
                        "Completed": False,
                        "TaskOrder": task_order
                    })

                for rec in recommendations:
                    links_ref = db.collection('TopicsTheoryRecommendations').document()
                    links_ref.set({
                        "TheoryID": topic_theory_id,
                        "Source": rec
                    })

                section_progress["Topics"].append(topic_progress)

            module_progress["Sections"].append(section_progress)

        user_course_progress["CourseCompletion"].append(module_progress)

    # Save the UserCourseProgress
    user_course_progress_ref = db.collection('UserCourseProgress').document()
    user_course_progress_ref.set(user_course_progress)

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

    # Fetch user progress data
    user_progress_ref = db.collection('UserCourseProgress').where("CourseID", "==", course_id).stream()
    user_progress_data = {}

    for progress in user_progress_ref:
        progress_data = progress.to_dict()
        course_completion = progress_data.get("CourseCompletion", [])

        for module in course_completion:
            module_id = module.get("ModuleID")
            module_order = module.get("ModuleOrder")
            module_completed = module.get("Completed", False)
            module_sections = module.get("Sections", [])

            if module_id:
                user_progress_data[module_id] = {
                    "Completed": module_completed,
                    "ModuleOrder": module_order,
                    "Sections": {}
                }

                for section in module_sections:
                    section_id = section.get("SectionID")
                    section_order = section.get("SectionOrder")
                    section_completed = section.get("Completed", False)

                    if section_id:
                        user_progress_data[module_id]["Sections"][section_id] = {
                            "Completed": section_completed,
                            "SectionOrder": section_order
                        }

    for module in course_modules:
        module_data = module.to_dict()
        module_id = module.id

        # Get module progress info
        module_progress = user_progress_data.get(module_id, {})
        module_order = module_progress.get("ModuleOrder", module_data.get("ModuleOrder"))
        module_completion = module_progress.get("Completed", False)

        sections_data = []
        sections = db.collection('CourseSections').where("ModuleID", "==", module_id).stream()
        for section in sections:
            section_data = section.to_dict()
            section_id = section.id

            # Get section progress info
            section_progress = module_progress.get("Sections", {}).get(section_id, {})
            section_order = section_progress.get("SectionOrder", section_data.get("SectionOrder"))
            section_completion = section_progress.get("Completed", False)

            sections_data.append({
                "id": section_id,
                "title": section_data["SectionTitle"],
                "order": section_order,
                "completion": section_completion
            })

        module_info = {
            "id": module_id,
            "title": module_data["ModuleTitle"],
            "order": module_order,
            "completion": module_completion,
            "sections": sections_data
        }
        modules_data.append(module_info)

    # Sort modules and sections by order
    modules_data = sorted(modules_data, key=lambda x: x["order"])
    for module in modules_data:
        module["sections"] = sorted(module["sections"], key=lambda x: x["order"])

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

@app.route("/get_topic_details/<topic_id>", methods=["GET"])
def get_topic_details(topic_id):
    topic_data = {}

    # Get topic data from CourseTopics
    topic_doc = db.collection('CourseTopics').document(topic_id).get()
    if topic_doc.exists:
        topic_data = topic_doc.to_dict()

    # Get theory data from CourseTopicsTheory
    theory_data = []
    theory_docs = db.collection('CourseTopicsTheory').where("TopicID", "==", topic_id).stream()
    for theory_doc in theory_docs:
        theory_dict = theory_doc.to_dict()
        theory_dict['id'] = theory_doc.id
        theory_data.append(theory_dict)

    # Get tasks data from TopicsTheoryTasks
    tasks_data = []
    for theory in theory_data:
        theory_id = theory['id']
        tasks = db.collection('TopicsTheoryTasks').where("TheoryID", "==", theory_id).stream()
        tasks_data.extend([task.to_dict() for task in tasks])

    if topic_data:
        topic_data['theory'] = theory_data
        topic_data['tasks'] = tasks_data
        return jsonify({"topics_theory_tasks": topic_data}), 200
    else:
        return jsonify({"message": "Topic not found"}), 404



@app.route("/topic_completed/<topic_id>/<user_id>", methods=["POST"])
def mark_topic_completed(topic_id, user_id):
    try:
        # Get user ID from request (replace with your authentication mechanism)

        # Check if topic exists
        topic_doc = db.collection('CourseTopics').document(topic_id).get()
        if not topic_doc.exists:
            return jsonify({"message": "Topic not found"}), 404

        # Check if topic has a section ID
        if "SectionID" not in topic_doc.to_dict():
            return jsonify({"message": "Topic doesn't have a section ID"}), 400

        # Get section ID from topic data
        section_id = topic_doc.to_dict()["SectionID"]

        # Get CourseSection document
        section_doc = db.collection('CourseSections').document(section_id).get()
        if not section_doc.exists:
            return jsonify({"message": "Section not found"}), 404

        # Extract module ID from CourseSection document
        module_id = section_doc.to_dict()["ModuleID"]

        # Update user progress document for the course
        user_progress_ref = db.collection('UserProgress').document(user_id)
        user_progress_doc = user_progress_ref.get()

        # Create new user progress document if it doesn't exist
        if not user_progress_doc.exists:
            user_progress_ref.set({
                "user_id": user_id,  # Include user_id in the progress document
                "modules": {}  # Dictionary to store progress for each module
            })
            user_progress_doc = user_progress_ref.get()

        user_progress = user_progress_doc.to_dict()["modules"]

        # Update section progress (mark topic completed)
        if module_id not in user_progress:
            user_progress[module_id] = {"sections": {}}
        if section_id not in user_progress[module_id]["sections"]:
            user_progress[module_id]["sections"][section_id] = {"topics": {}}
        user_progress[module_id]["sections"][section_id]["topics"][topic_id] = True

        # Check if this was the last topic in the section
        section_topics = db.collection('CourseTopics').where("SectionID", "==", section_id).get()
        section_topics_completed = all(user_progress[module_id]["sections"][section_id]["topics"].get(topic.id, False) for topic in section_topics)

        if section_topics_completed:
            # Mark the section as completed
            user_progress[module_id]["sections"][section_id]["completed"] = True

            # Check if this was the last section in the module
            module_sections = db.collection('CourseSections').where("ModuleID", "==", module_id).get()
            module_sections_completed = all(user_progress[module_id]["sections"].get(section.id, {}).get("completed", False) for section in module_sections)

            if module_sections_completed:
                # Mark the module as completed
                user_progress[module_id]["completed"] = True

        # Update user progress document
        user_progress_ref.update({"modules": user_progress})

        return jsonify({"message": "Topic completion saved successfully"}), 200

    except Exception as e:
        print(f"Error marking topic completed: {e}")
        return jsonify({"message": "An error occurred while marking topic completed"}), 500


@app.route("/check_topic_completion/<topic_id>/<user_id>", methods=["GET"])
def check_topic_completion(topic_id, user_id):
    try:
        # Get the user progress document
        user_progress_ref = db.collection('UserProgress').document(user_id)
        user_progress_doc = user_progress_ref.get()

        # If the user progress document doesn't exist, the topic is not completed
        if not user_progress_doc.exists:
            return jsonify({"completed": False}), 200

        user_progress = user_progress_doc.to_dict()["modules"]

        # Iterate through modules and sections to check if the topic is marked as completed
        for module_id, module_data in user_progress.items():
            sections = module_data.get("sections", {})
            for section_id, section_data in sections.items():
                topics = section_data.get("topics", {})
                if topic_id in topics and topics[topic_id]:
                    return jsonify({"completed": True}), 200

        return jsonify({"completed": False}), 200

    except Exception as e:
        print(f"Error checking topic completion: {e}")
        return jsonify({"message": "An error occurred while checking topic completion"}), 500
    

@app.route("/get_user_progress/<user_id>/<course_id>", methods=["GET"])
def get_user_progress(user_id, course_id):
    try:
        # Get the user progress document where "user_id" is equal to the provided user_id
        user_progress_ref = db.collection('UserProgress').where("user_id", "==", user_id).limit(1).get()

        print(user_progress_ref)
        # If no user progress document is found, return an empty progress
        if not user_progress_ref:
            return jsonify({"modules": {}}), 200

        # Get the first document in the result (there should be only one)
        user_progress_doc = user_progress_ref[0]

        # Get the progress data
        user_progress = user_progress_doc.to_dict()["modules"]

        # Filter the progress data to only include the specified course
        course_progress = {}
        for module_id, module_data in user_progress.items():
            course_progress[module_id] = module_id

        return jsonify({"modules": course_progress}), 200

    except Exception as e:
        print(f"Error fetching user progress: {e}")
        return jsonify({"message": "An error occurred while fetching user progress"}), 500






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