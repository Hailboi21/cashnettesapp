from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)

class Demande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    adresse = db.Column(db.String(200))
    emplacement = db.Column(db.String(200))
    moment = db.Column(db.String(100))
    acces = db.Column(db.String(200))
    heure_limite = db.Column(db.String(50))
    notes = db.Column(db.Text)