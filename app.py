import os
import json
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="dist", static_url_path="")

CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///animals.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), "pet_images")
os.makedirs(IMAGES_FOLDER, exist_ok=True)


# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user") # "user" или "admin"
    first_name = db.Column(db.String(50), default="Пользователь")
    last_name = db.Column(db.String(50), default="")
    birth_date = db.Column(db.String(20), default="")
    work_field = db.Column(db.String(100), default="")
    hobbies = db.Column(db.String(200), default="")
    about = db.Column(db.Text, default="")
    avatar = db.Column(db.Text, default="")


class UserContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False) # "email" или "phone"
    value = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), default="")
    status = db.Column(db.String(20), default="pending") # "verified" или "pending"
    is_primary = db.Column(db.Boolean, default=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    options_json = db.Column(db.Text, default="[]") # JSON-массив вариантов или пустой []


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


# ==================== ОТДАЧА КАРТИНОК ====================

@app.route("/api/images/<filename>")
def serve_pet_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)


# ==================== АВТОРИЗАЦИЯ ====================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Этот email уже зарегистрирован"}), 400

    role = "admin" if data["email"] == "admin@fond-nika.ru" else "user"
    user = User(
        email=data["email"],
        password=data["password"],
        first_name=data.get("name") or "Пользователь",
        role=role

)
    db.session.add(user)
    db.session.add(UserContact(
        user_email=user.email,
        type="email",
        value=user.email,
        subtitle="Почта, основная: письма, чеки и вход",
        status="verified",
        is_primary=True
    ))
    db.session.commit()
    return jsonify({"token": f"token-{user.id}", "email": user.email, "role": user.role})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"], password=data["password"]).first()
    if not user:
        return jsonify({"error": "Неверный логин или пароль"}), 401
    return jsonify({"token": f"token-{user.id}", "email": user.email, "role": user.role})


# ==================== ПРОФИЛЬ ====================

@app.route("/api/profile", methods=["GET", "PUT"])
def handle_profile():
    if request.method == "GET":
        email = request.args.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404

        contacts = UserContact.query.filter_by(user_email=email).all()
        quiz = QuizResult.query.filter_by(user_email=email).first()
        fav_ids = [f.pet_id for f in Favorite.query.filter_by(user_email=email).all()]
        fav_pets = Pet.query.filter(Pet.id.in_(fav_ids)).all()

        return jsonify({
            "profile": {
                "firstName": user.first_name,
                "lastName": user.last_name,
                "birthDate": user.birth_date,
                "workField": user.work_field,
                "hobbies": user.hobbies,
                "about": user.about,
                "avatar": user.avatar
            },
            "contacts": [
                {
                    "id": c.id,
                    "type": c.type,
                    "value": c.value,
                    "subtitle": c.subtitle,
                    "status": c.status,
                    "isPrimary": c.is_primary
                } for c in contacts
            ],
            "quizResults": json.loads(quiz.answers_json) if quiz else [],
            "favorites": [
                {
                    "id": p.id,
                    "name": p.name,
                    "age": p.age,
                    "description": p.description,
                    "guardians": p.guardians,
                    "image": p.image
                } for p in fav_pets
            ]
        })

    if request.method == "PUT":
        data = request.get_json()
        email = data.get("email")
        p = data.get("profile", {})
        user = User.query.filter_by(email=email).first()

        if user:
            user.first_name = p.get("firstName", user.first_name)
            user.last_name = p.get("lastName", user.last_name)
            user.birth_date = p.get("birthDate", user.birth_date)
            user.work_field = p.get("workField", user.work_field)
            user.hobbies = p.get("hobbies", user.hobbies)
            user.about = p.get("about", user.about)
            user.avatar = p.get("avatar", user.avatar)

        if "contacts" in data:
            UserContact.query.filter_by(user_email=email, is_primary=False).delete()
            for c in data["contacts"]:
                if not c.get("isPrimary"):
                    db.session.add(UserContact(
                        user_email=email,
                        type=c["type"],
                        value=c["value"],
                        subtitle=c.get("subtitle", ""),
                        status=c.get("status", "pending"),
                        is_primary=False
                    ))

        db.session.commit()
        return jsonify({"status": "saved"})
# ==================== ОПРОС ====================

@app.route("/api/questions", methods=["GET"])
def get_questions():
    items = Question.query.all()
    return jsonify([
        {
            "id": q.id,
            "text": q.text,
            "options": json.loads(q.options_json)
        } for q in items
    ])

@app.route("/api/quiz", methods=["POST"])
def save_quiz():
    data = request.get_json()
    email = data.get("email")
    answers_str = json.dumps(data.get("answers", []), ensure_ascii=False)

    existing = QuizResult.query.filter_by(user_email=email).first()
    if existing:
        existing.answers_json = answers_str
    else:
        db.session.add(QuizResult(user_email=email, answers_json=answers_str))

    db.session.commit()
    return jsonify({"status": "ok"})


# ==================== ПОДБОР ПИТОМЦЕВ + МЕСТО ДЛЯ LLM ====================
# максим???????????????????????
def match_pets_with_llm(user_answers, all_pets):
    """
    Заглушка для будущей LLM.
    Когда подключите нейросеть:
    1. Передайте в промпт user_answers и список all_pets.
    2. Получите от LLM отсортированный список ID подходящих животных и поле ai_reason.
    """
    result = []
    for p in all_pets:
        reason = "Отлично подойдет под ваш ритм жизни и условия проживания." if user_answers else ""
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "description": p.description,
            "guardians": p.guardians,
            "image": p.image,
            "ai_reason": reason
        })
    return result


@app.route("/api/pets", methods=["GET"])
def get_pets():
    email = request.args.get("email")
    quiz = QuizResult.query.filter_by(user_email=email).first()
    user_answers = json.loads(quiz.answers_json) if quiz else []
    all_pets = Pet.query.all()

    matched_pets = match_pets_with_llm(user_answers, all_pets)
    return jsonify(matched_pets)


# ==================== ИЗБРАННОЕ ====================

@app.route("/api/favorites", methods=["GET", "POST"])
def handle_favorites():
    if request.method == "GET":
        email = request.args.get("email")
        fav_ids = [f.pet_id for f in Favorite.query.filter_by(user_email=email).all()]
        pets = Pet.query.filter(Pet.id.in_(fav_ids)).all()
        return jsonify([
            {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "description": p.description,
                "guardians": p.guardians,
                "image": p.image
                } for p in pets
                ])
        if request.method == "POST":
            data = request.get_json()
        exists = Favorite.query.filter_by(user_email=data["email"], pet_id=data["pet_id"]).first()
        if not exists:
            db.session.add(Favorite(user_email=data["email"], pet_id=data["pet_id"]))
        db.session.commit()
        return jsonify({"status": "added"})
@app.route("/api/favorites/int:pet_id", methods=["DELETE"])
def delete_favorite(pet_id):
    email = request.args.get("email")
    Favorite.query.filter_by(user_email=email, pet_id=pet_id).delete()
    db.session.commit()
    return jsonify({"status": "deleted"})


# ==================== ЗАЯВКИ "ПРИЮТИТЬ" (АДМИНКА) ====================
@app.route("/api/requests", methods=["GET", "POST"])
def handle_requests():
    if request.method == "GET":
        reqs = AdoptRequest.query.order_by(AdoptRequest.id.desc()).all()
    result = []
    for r in reqs:
        pet = db.session.get(Pet, r.pet_id)
    result.append({
    "id": r.id,
    "petId": r.pet_id,
    "petName": pet.name if pet else "Питомец",
    "petDescription": pet.description if pet else "",
    "petImage": pet.image if pet else "",
    "applicantName": r.applicant_name,
    "contact": r.contact,
    "contactMethod": r.contact_method,
    "status": r.status,
    "createdAt": r.created_at
    })
    return jsonify(result)
    if request.method == "POST":
        data = request.get_json()
    new_req = AdoptRequest(
    pet_id=data["pet_id"],
    applicant_name=data["applicant_name"],
    contact=data["contact"],
    contact_method=data["contact_method"],
    status="new",
    created_at=datetime.now().strftime("%d.%m.%Y, %H:%M")
    )
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"status": "created"})
@app.route("/api/requests/int:req_id", methods=["PATCH", "DELETE"])
def modify_request(req_id):
    req_item = db.session.get(AdoptRequest, req_id)
    if not req_item:
        return jsonify({"error": "Заявка не найдена"}), 404
    if request.method == "PATCH":
        data = request.get_json()
    req_item.status = data.get("status", req_item.status)
    db.session.commit()
    return jsonify({"status": "updated"})
    if request.method == "DELETE":
        db.session.delete(req_item)
        db.session.commit()
        return jsonify({"status": "deleted"})
    
    
# ==================== РАЗДАЧА VUE (SPA FALLBACK) ====================
@app.route("/", defaults={"path": ""})
@app.route("/path:path")
def serve_vue(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")
# ==================== ЗАПУСК И НАЧАЛЬНОЕ НАПОЛНЕНИЕ БД ====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

app.run(debug=True)