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
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def envoyer_discord(message):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"Erreur Discord : {e}")

# =========================
# SECTEUR DESSERVI (CORRIGÉ)
# =========================
SECTEUR_E = [
    "rue saint-pierre", "boulevard st-joseph", "rue saint-jean", "rue saint-damase", "rue manseau",
    "rue saint-alphonse", "rue saint-frédéric", "rue mélançon", "rue marchand",
    "rue bruno", "rue cockburn", "rue surprenant", "rue rajotte", "rue savard", "rue faucher",
    "rue désilet","rue saint-antoine", "rue saint-marc", "rue saint-ambroise",
    "rue villeneuve", "rue saint-paul", "rue saint-lucien", "rue saint-marcel", "rue saint-albert",
    "rue sylvain", "rue saint-alfred", "rue turcotte", "rue du drapeau",
    "rue notre-dame", "rue ringuet", "rue pelletier", "rue ferland", "rue chassé", "rue mathieu",
    "6e avenue", "7e avenue", "8e avenue", "9e avenue", "10e avenue", "11e avenue",
    "12e avenue", "13e avenue", "14e avenue", "15e avenue", "16e avenue", "17e avenue",
    "18e avenue", "19e avenue", "20e avenue", "21e avenue", "22e avenue",
    "rue bernabé", "rue croteau", "rue lauzière", "rue milette","rue saint-eusèbes",
    "rue celanese", "rue du velours", "rue camille dreyfus", "rue du satin", "rue biron", "rue gendron", "rue gill",
    "rue raphaelle-nolet","rue paillé", "rue jaques-desautels", "rue mauchon", "rue beaudoins", "rue dumaine",
    "rue bessette", "rue fortin","rue oscar-thiffault", "rue precourt", "rue desjardins", "rue lalemant", "goupil",
    "rue jogues", "rue jean de lalande", "rue saint-thomas", "rue saint-edgar", "rue de l'étoffe", "rue de l'écru",
    "rue du denier", "rue de la navette"
]

# =========================
# ROUTES
# =========================

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        nom = request.form.get("nom")
        
        # Récupération séparée
        unite = request.form.get("unite", "").strip()
        rue = request.form.get("rue", "").lower()
        
        # On reconstitue l'adresse complète pour la base de données
        adresse = f"{unite} {rue}"
        
        emplacement = request.form.get("emplacement")
        moment = request.form.get("moment")
        acces = request.form.get("acces")
        heure_limite = request.form.get("heure_limite")
        notes = request.form.get("notes")

        # Vérification sur la rue choisie dans le menu
        if rue not in SECTEUR_E:
            return render_template("error.html", message="Désolé, cette rue n'est pas desservie.")

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
    
    # Envoi de la liste triée vers index.html
    return render_template("index.html", secteurs=sorted(SECTEUR_E))

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