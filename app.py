import os
from datetime import temedelta
from flask_jwt_extended import JWTManager, create_access_token
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///animals.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")
    

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(20), nullable = False)
    home = db.Column(db.String(20), nullable = False)

 
@app.route("/")
def home():
    return render_template("questions.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "заполните все поля"}), 400
    user = User.query.filter_by(email=email).first()
    if user:
        return {"error": "Пользователь уже зарегестрирован"}, 409
    new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"аккаунт успешно создан", "email": new_user.email, "role": new_user.role}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Некорректно"}), 400
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "заполните все поля"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Неверный email или пароль"}), 401
    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Неверный email или пароль"}), 401    
    return 

@app.route("/submit", methods=["POST"])
def submit():
    animal = request.form["animal"]
    home = request.form["home"]
    if animal not in ["cat", "dog"] or home not in ["apartment", "house"]:
        return "wth", 400
    new_response = Questionnaire(animal=animal, home=home)
    db.session.add(new_response)
    db.session.commit()
    
    return f"u want a {animal} and live in {home}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)