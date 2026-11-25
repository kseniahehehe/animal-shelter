import os
from datetime import timedelta
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
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), default="")
    birth_date = db.Column(db.String(20), default="")
    work_field = db.Column(db.String(100), default="")
    hobbies = db.Column(db.String(200), default="")
    about = db.Column(db.Text, default="")
    avatar = db.Column(db.Text, default="")
    
class UserContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False) 
    value = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), default="")
    status = db.Column(db.String(20), default="pending") 
    is_primary = db.Column(db.Boolean, default=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    options_json = db.Column(db.Text, default="[]")
    
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    answers_json = db.Column(db.Text, nullable=False)
    
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    guardians = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(300), nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    
class AdoptRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    contact_method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default="new")
    created_at = db.Column(db.String(30), nullable=False)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Flask работает"
    })
 
 
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
    
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": token,
        "email": user.email,
        "role": user.role
    }), 200
    
    
    @app.route ("api/profile", methods=["GET", "PUT"])
    def handle_profile():
        if request.method == "GET":
            email = request.args.get("email")
            user = User.query.filter_by(user_email=email).first()
            if not user:
                return jsonify({"error": "пользователь не найден"}), 404
            
    



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)