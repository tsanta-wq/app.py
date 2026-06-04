from flask import Flask, render_template_string, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# CONFIGURATION DE TON COMPTE GMAIL (POUR RECEVOIR)
EMAIL_RECEVEUR = "millihenri1@gmail.com"
EMAIL_ENVOYEUR = "millihenri1@gmail.com"
# Mets ici tes 16 lettres en jaune générées sur Google (tout attaché)
EMAIL_PASS = "sxiohhobinwrfsyc"

def envoyer_email(nom_visiteur, email_visiteur, message_visiteur):
    try:
        # Configuration du serveur de messagerie de Google
        serveur = smtplib.SMTP("smtp.gmail.com", 587)
        serveur.starttls()  # Sécurisation de la connexion
        serveur.login(EMAIL_ENVOYEUR, EMAIL_PASS)

        # Création du contenu du mail
        sujet = f"Nouveau message de {nom_visiteur} depuis ton site"
        corps_du_mail = f"""
        Tu as reçu un nouveau message !
        
        Nom du visiteur : {nom_visiteur}
        Email du visiteur : {email_visiteur}
        
        Message :
        {message_visiteur}
        """

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ENVOYEUR
        msg['To'] = EMAIL_RECEVEUR
        msg['Subject'] = sujet
        msg.attach(MIMEText(corps_du_mail, 'plain', 'utf-8'))

        # Envoi effectif
        serveur.sendmail(EMAIL_ENVOYEUR, EMAIL_RECEVEUR, msg.as_string())
        serveur.quit()
        return True
    except Exception as e:
        print(f"Erreur d'envoi : {e}")
        return False

# DESIGN : INTERFACE D'INVITE D'ENVOI DE MESSAGE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Envoyer un message</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
        .form-container { max-width: 550px; margin: 60px auto; background: white; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); overflow: hidden; }
        .form-header { background-color: #007bff; color: white; padding: 20px; font-size: 1.25rem; font-weight: bold; text-center }
        .form-body { padding: 30px; }
        .btn-send { background-color: #007bff; color: white; width: 100%; border-radius: 8px; padding: 10px; font-weight: bold; border: none; }
        .btn-send:hover { background-color: #0056b3; }
    </style>
</head>
<body>
<div class="container">
    <div class="form-container">
        <div class="form-header text-center">
            💬 Nouvelle invite de message
        </div>
        <div class="form-body">
            {% if statut == 'success' %}
                <div class="alert alert-success text-center">✉️ Message envoyé avec succès sur ta boîte mail !</div>
            {% elif statut == 'error' %}
                <div class="alert alert-danger text-center">❌ Erreur lors de l'envoi. Vérifie ton mot de passe d'application.</div>
            {% endif %}

            <form action="/envoyer" method="POST">
                <div class="mb-3">
                    <label class="form-label font-weight-bold">Votre Nom</label>
                    <input type="text" name="nom" class="form-control" placeholder="Ex: Jean" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Votre Adresse Email</label>
                    <input type="email" name="email_visiteur" class="form-control" placeholder="Ex: visiteur@gmail.com" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Message</label>
                    <textarea name="message" class="form-control" rows="5" placeholder="Écrivez votre message ici..." required></textarea>
                </div>
                <button type="submit" class="btn-send">Envoyer le message 🚀</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    statut = request.args.get('statut')
    return render_template_string(HTML_TEMPLATE, statut=statut)

@app.route('/envoyer', methods=['POST'])
def envoyer():
    nom = request.form.get('nom')
    email_visiteur = request.form.get('email_visiteur')
    message = request.form.get('message')
    
    # Appel de la fonction SMTP pour envoyer le mail
    succes = envoyer_email(nom, email_visiteur, message)
    
    if succes:
        return redirect(url_for('index', statut='success'))
    else:
        return redirect(url_for('index', statut='error'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
