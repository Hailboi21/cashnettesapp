import os
import requests
from flask import Flask, render_template, request
from database import db, Demande

app = Flask(__name__)
# Utilisation d'une variable d'environnement pour la clé secrète (plus sécurisé)
app.secret_key = os.environ.get('SECRET_KEY', 'votre_cle_secrete_par_defaut')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashnettes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

SECTEUR_7 = ["saint-pierre", "boulevard st-joseph", "saint-jean","saint-damase","manseau","saint-alphonse","saint-frédéric","mélancon","mélançon","marchand","bruno","cockburn","surprenant","rajotte","savard","faucher","désilet","desilet","saint-antoine","saint-marc","saint-ambroise","villeneuve","saint-paul","saint-lucien","saint-marcel","saint-albert","sylvain","saint-alfred","turcotte","du drapeau","notre dame","notre-dame","ringuet","pelletier","ferland","chassé","mathieu","6e avenue","6eme avenue","7e avenue","7eme avenue","8e avenue","8eme avanue","9e avenue","9eme avanue"]

def envoyer_discord(message):
    webhook_url = "https://discord.com/api/webhooks/1515568361684078683/KHe3L5YkczRBB2liyZbCb5Gho-DQ8fWKmq1pgOEmgYLPjXNgr2NNGsHPdQKKUOpDzrkD"
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"Erreur lors de l'envoi Discord : {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Récupération des données
        nom = request.form.get('nom')
        adresse = request.form.get('adresse', '').lower()
        emplacement = request.form.get('emplacement')
        moment = request.form.get('moment')
        acces = request.form.get('acces')
        heure_limite = request.form.get('heure_limite')
        notes = request.form.get('notes')

        # Sauvegarde en base de données
        nouvelle_demande = Demande(nom=nom, adresse=adresse, emplacement=emplacement, 
                                   moment=moment, acces=acces, heure_limite=heure_limite, notes=notes)
        db.session.add(nouvelle_demande)
        db.session.commit()

        # Notification Discord
        notification = (f"🚨 **Nouvelle demande Cashnettes !**\n👤 {nom}\n🏠 {adresse}\n📍 {emplacement}\n"
                        f"📅 {moment}\n🔑 {acces}\n⏰ {heure_limite}\n📝 {notes}")
        envoyer_discord(notification)

        # Remplacement de la page blanche par votre page de confirmation stylisée
        return render_template('confirmation.html')

    return render_template('index.html', rues=SECTEUR_7)

@app.route('/admin')
def admin():
    toutes_les_demandes = Demande.query.all()
    return render_template('admin.html', demandes=toutes_les_demandes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Le run sans paramètres host/port permet à Render de gérer la connexion automatiquement
    app.run()