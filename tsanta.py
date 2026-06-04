from flask import Flask, render_template_string, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# CONFIGURATION DE TON COMPTE GMAIL (SERVIRE DE PASSERELLE)
EMAIL_COMPTE = "millihenri1@gmail.com"
# Colle tes 16 lettres ici (tout attaché, sans espaces, en minuscules)
EMAIL_PASS = "sxiohhobinwrfsyc" 

def envoyer_email(nom_visiteur, email_visiteur, message_visiteur):
    try:
        # Connexion sécurisée au serveur SMTP de Google avec TES identifiants
        serveur = smtplib.SMTP("smtp.gmail.com", 587)
        serveur.starttls()
        serveur.login(EMAIL_COMPTE, EMAIL_PASS)

        # Structure du mail : C'est TOI qui t'envoies le mail à toi-même
        sujet = f"Nouveau message de {nom_visiteur} depuis ton site"
        corps_du_mail = f"""
        Tu as reçu un nouveau message de la part d'un visiteur !
        
        Nom du visiteur : {nom_visiteur}
        Email pour lui répondre : {email_visiteur}
        
        --------------------------------------------------
        Message :
        {message_visiteur}
        --------------------------------------------------
        """

        msg = MIMEMultipart()
        msg['From'] = EMAIL_COMPTE
        msg['To'] = EMAIL_COMPTE  # Tu le reçois sur ta propre boîte
        msg['Subject'] = sujet
        msg.attach(MIMEText(corps_du_mail, 'plain', 'utf-8'))

        # Envoi du message
        serveur.sendmail(EMAIL_COMPTE, EMAIL_COMPTE, msg.as_string())
        serveur.quit()
        return True
    except Exception as e:
        print(f"Erreur technique d'envoi : {e}")
        return False

# INTERFACE DU FORMULAIRE DE CONTACT
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laisser un message à Tsanta</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
        .form-container { max-width: 550px; margin: 60px auto; background: white; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); overflow: hidden; }
        .form-header { background-color: #007bff; color: white; padding: 20px; font-size: 1.25rem; font-weight: bold; }
        .form-body { padding: 30px; }
        .btn-send { background-color: #007bff; color: white; width: 100%; border-radius: 8px; padding: 10px; font-weight: bold; border: none; }
        .btn-send:hover { background-color: #0056b3; }
    </style>
</head>
<body>
<div class="container">
    <div class="form-container">
        <div class="form-header text-center">
            💬 Envoyer un message à Tsanta
        </div>
        <div class="form-body">
            {% if statut == 'success' %}
                <div class="alert alert-success text-center">✉️ Votre message a bien été envoyé !</div>
            {% elif statut == 'error' %}
                <div class="alert alert-danger text-center">❌ Une erreur est survenue lors de l'envoi.</div>
            {% endif %}

            <form action="/envoyer" method="POST">
                <div class="mb-3">
                    <label class="form-label">Votre Nom</label>
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
    
    succes = envoyer_email(nom, email_visiteur, message)
    
    if succes:
        return redirect(url_for('index', statut='success'))
    else:
        return redirect(url_for('index', statut='error'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
