from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# =========================
# 👤 CLIENT
# =========================
class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(
        db.String(100),
        nullable=False
    )

    adresse = db.Column(
        db.String(200),
        nullable=False
    )

    # Relation : un client possède plusieurs tickets
    tickets = db.relationship(
        "Ticket",
        backref="client",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client {self.nom}>"

# =========================
# 🎫 TICKET
# =========================
class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id"),
        nullable=False
    )

    sujet = db.Column(
        db.String(200),
        default="Nouvelle demande"
    )

    statut = db.Column(
        db.String(50),
        default="open"
    )

    emplacement = db.Column(
        db.String(200)
    )

    moment = db.Column(
        db.String(100)
    )

    acces = db.Column(
        db.String(200)
    )

    heure_limite = db.Column(
        db.String(50)
    )

    notes = db.Column(
        db.Text
    )

    # Relation : un ticket possède plusieurs messages
    messages = db.relationship(
        "Message",
        backref="ticket",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ticket #{self.id}>"

# =========================
# 💬 MESSAGE
# =========================
class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ticket.id"),
        nullable=False
    )

    sender = db.Column(
        db.String(50),
        nullable=False
    )
    # client / admin

    content = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<Message {self.id}>"

# =========================
# 📅 RENDEZ-VOUS
# =========================
class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_name = db.Column(
        db.String(100),
        nullable=False
    )

    date = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="requested"
    )
    # requested / accepted / rejected

    def __repr__(self):
        return f"<Appointment {self.client_name}>"