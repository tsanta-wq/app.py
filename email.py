from flask import Flask, render_template_string
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

# CONFIGURATION UNIQUE POUR TON COMPTE GMAIL
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = "millihenri1@gmail.com"
# Colle tes 16 lettres ici à la place du texte ci-dessous (ex: "abcdefghijklmnop")
EMAIL_PASS = "sxiohhobinwrfsyc" 

def recuperer_messages():
    messages_liste = []
    try:
        # Connexion sécurisée à Gmail via le protocole IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Récupération des 5 derniers messages reçus dans la boîte principale
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        for i in reversed(email_ids[-5:]):
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Décodage propre du Sujet de l'email
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    
                    # Décodage propre de l'Expéditeur
                    from_, encoding = decode_header(msg["From"])[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding or "utf-8", errors="ignore")
                    
                    # Extraction du contenu textuel de l'email
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    # Ajout du dictionnaire dans notre liste d'affichage
                    messages_liste.append({
                        "from": from_,
                        "subject": subject,
                        "body": body[:150] + "..." if len(body) > 150 else body
                    })
        mail.logout()
    except Exception as e:
        # En cas d'erreur de mot de passe ou de réseau, le message s'affichera sur le site
        messages_liste.append({
            "from": "Système de sécurité", 
            "subject": "Erreur de connexion", 
            "body": f"Impossible de se connecter à millihenri1@gmail.com. Vérifie ton mot de passe d'application. Détails : {e}"
        })
    
    return messages_liste

# DESIGN SUR MESURE : INTERFACE BANDEAU ET BULLES D'INVITE DE MESSAGE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invite de Messages - millihenri1</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background-color: #f4f6f9; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .chat-container { 
            max-width: 750px; 
            margin: 40px auto; 
            background: white; 
            border-radius: 16px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.08); 
            overflow: hidden; 
        }
        .chat-header { 
            background-color: #007bff; 
            color: white; 
            padding: 20px; 
            font-size: 1.2rem; 
            font-weight: 600; 
        }
        .message-box { 
            padding: 25px; 
            max-height: 650px; 
            overflow-y: auto; 
        }
        .message-card { 
            background-color: #f8f9fa; 
            border-radius: 12px; 
            padding: 18px; 
            margin-bottom: 20px; 
            border-left: 5px solid #007bff; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        .message-sender { 
            font-weight: bold; 
            color: #212529; 
            font-size: 0.95rem; 
        }
        .message-subject { 
            font-style: italic; 
            color: #6c757d; 
            font-size: 0.88rem;
            margin-top: 2px;
        }
        .message-body { 
            font-size: 0.95rem; 
            color: #495057; 
            white-space: pre-line; 
            margin-top: 10px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="chat-container">
        <div class="chat-header d-flex justify-content-between align-items-center">
            <span>📥 Boîte de Réception : millihenri1@gmail.com</span>
            <button class="btn btn-sm btn-light" onclick="window.location.reload();">Actualiser</button>
        </div>
        
        <div class="message-box">
            {% for email in emails %}
            <div class="message-card">
                <div class="message-sender">De : {{ email.from }}</div>
                <div class="message-subject">Sujet : {{ email.subject }}</div>
                <hr class="my-2" style="color: #dee2e6;">
                <div class="message-body">{{ email.body }}</div>
            </div>
            {% else %}
            <div class="text-center text-muted py-4">Aucun message trouvé ou actualisation nécessaire.</div>
            {% endfor %}
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    # Appel de la fonction IMAP au chargement de la page
    emails = recuperer_messages()
    return render_template_string(HTML_TEMPLATE, emails=emails)

if __name__ == '__main__':
    # Configuration universelle pour tourner en local ou être reliée à un tunnel (ex: Ngrok)
    app.run(host='0.0.0.0', port=5000, debug=True)
