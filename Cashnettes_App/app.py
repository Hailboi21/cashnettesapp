import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from database import db, Client, Ticket, Message

app = Flask(__name__)

# =========================
# CONFIG
# =========================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cashnettes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "votre_cle_secrete"

db.init_app(app)

# CRÉATION DES TABLES AU DÉMARRAGE
with app.app_context():
    db.create_all()

# =========================
# DISCORD
# =========================
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1515671283608850623/vFF_V_4o2DVysNCixpXJESxEPHcV708x-GF_ZdM1u38RPCW9u04_usXfvJeGSiZqXGVg"

def envoyer_discord(message):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"Erreur Discord : {e}")

# =========================
# SECTEUR DESSERVI
# =========================
SECTEUR_7 = [
    "saint-pierre", "boulevard st-joseph", "saint-jean", "saint-damase", "manseau",
    "saint-alphonse", "saint-frédéric", "mélancon", "mélançon", "marchand",
    "bruno", "cockburn", "surprenant", "rajotte", "savard", "faucher",
    "désilet", "desilet", "saint-antoine", "saint-marc", "saint-ambroise",
    "villeneuve", "saint-paul", "saint-lucien", "saint-marcel", "saint-albert",
    "sylvain", "saint-alfred", "turcotte", "du drapeau", "notre dame",
    "notre-dame", "ringuet", "pelletier", "ferland", "chassé", "mathieu",
    "6e avenue", "7e avenue", "8e avenue", "9e avenue"
]

# =========================
# ROUTES (Toutes tes routes conservées)
# =========================

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        nom = request.form.get("nom")
        adresse = request.form.get("adresse", "").lower()
        emplacement = request.form.get("emplacement")
        moment = request.form.get("moment")
        acces = request.form.get("acces")
        heure_limite = request.form.get("heure_limite")
        notes = request.form.get("notes")

        if not any(rue in adresse for rue in SECTEUR_7):
            return render_template("error.html", message="Désolé, nous ne desservons pas encore votre secteur.")

        client = Client.query.filter_by(nom=nom, adresse=adresse).first()
        if not client:
            client = Client(nom=nom, adresse=adresse)
            db.session.add(client)
            db.session.flush()

        ticket = Ticket(
            client_id=client.id, sujet="Nouvelle demande", emplacement=emplacement,
            moment=moment, acces=acces, heure_limite=heure_limite, notes=notes, statut="open"
        )
        db.session.add(ticket)
        db.session.flush()

        premier_message = Message(ticket_id=ticket.id, sender="client", content=notes or "Nouvelle demande")
        db.session.add(premier_message)
        db.session.commit()

        envoyer_discord(f"🚨 Nouveau Ticket\n👤 {nom}\n🏠 {adresse}\n📍 {emplacement}\n📅 {moment}\n⏰ {heure_limite}\n📝 {notes}")

        return render_template("success.html", ticket=ticket)
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return render_template("dashboard.html", tickets=tickets)

@app.route("/admin/clients")
def admin_clients():
    clients = Client.query.all()
    return render_template("clients_admin.html", clients=clients)

@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    messages = Message.query.filter_by(ticket_id=ticket.id).all()
    return render_template("ticket.html", ticket=ticket, messages=messages)

@app.route("/ticket/<int:ticket_id>/reply", methods=["POST"])
def reply_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    content = request.form.get("message")
    if not content:
        return redirect(url_for("view_ticket", ticket_id=ticket.id))
    message = Message(ticket_id=ticket.id, sender="admin", content=content)
    db.session.add(message)
    ticket.statut = "pending"
    db.session.commit()
    envoyer_discord(f"💬 Réponse admin sur ticket #{ticket.id}\n{content}")
    return redirect(url_for("view_ticket", ticket_id=ticket.id))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)