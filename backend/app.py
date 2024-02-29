from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt #pip install Flask-Bcrypt = https://pypi.org/project/Flask-Bcrypt/
from flask_cors import CORS, cross_origin #ModuleNotFoundError: No module named 'flask_cors' = pip install Flask-Cors
from models import db, User, Profession


app = Flask(__name__)
 
app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
 
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
  
bcrypt = Bcrypt(app) 
CORS(app, supports_credentials=True, methods=["GET", "POST"])
db.init_app(app)
  
with app.app_context():
    db.create_all()





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

    return jsonify({"message": f"{model.__name__} added successfully"})
######



# User adding/viewing/modifying/deleting
@app.route("/get_users", methods=["GET"])
def get_users():
    return get_entities(User, "users", ["id", "email", "role_id"])

@app.route("/add_user", methods=["POST"])
def add_user():
    return add_entity(User, request, ["email", "password", "role_id"])
    

# Profession adding/viewing/modifying/deleting
@app.route("/get_prof", methods=["GET"])
def get_prof():
    return get_entities(Profession, "professions", ["id", "profession_name", "profession_description"])

@app.route("/add_prof", methods=["POST"])
def add_prof():
    return add_entity(Profession, request, ["profession_name", "profession_description"])

if __name__ == "__main__":
    app.run(debug=True)