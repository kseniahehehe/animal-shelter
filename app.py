from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///animals.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(20), nullable = False)
    home = db.Column(db.String(20), nullable = False)
 
@app.route("/")
def home():
    return render_template("questions.html")


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