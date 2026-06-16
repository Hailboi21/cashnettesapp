from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# =========================
# 👤 CLIENT
# =========================
class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=db.func.now())

    # relation automatique : client.tickets
    tickets = db.relationship("Ticket", backref="client", lazy=True)


# =========================
# 🎫 TICKET (remplace Demande)
# =========================
class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)

    sujet = db.Column(db.String(200))
    statut = db.Column(db.String(50), default="open")  
    # open / pending / closed

    emplacement = db.Column(db.String(200))
    moment = db.Column(db.String(100))
    acces = db.Column(db.String(200))
    heure_limite = db.Column(db.String(50))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.now())

    # relation automatique : ticket.messages
    messages = db.relationship("Message", backref="ticket", lazy=True, cascade="all, delete-orphan")


# =========================
# 💬 MESSAGE (chat client/admin)
# =========================
class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)

    sender = db.Column(db.String(50), nullable=False)
    # "client" ou "admin"

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())


# =========================
# 📅 RENDEZ-VOUS (option CRM)
# =========================
class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(db.Integer, primary_key=True)

    client_name = db.Column(db.String(100))
    date = db.Column(db.String(100))

    status = db.Column(db.String(50), default="requested")
    # requested / accepted / rejected

    created_at = db.Column(db.DateTime, default=db.func.now())