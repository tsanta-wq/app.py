from flask import Flask, render_template_string
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

# CONFIGURATION DE VOTRE COMPTE EMAIL
IMAP_SERVER = "imap.gmail.com"  # Utilisez "outlook.office365.com" pour Outlook
EMAIL_USER = "millihenri1@gmail.com "
EMAIL_PASS = "zfbaaheidjfsljnc" 

def recuperer_messages():
    messages_liste = []
    try:
        # Connexion au serveur IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Recherche des 5 derniers emails reçus
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        for i in reversed(email_ids[-5:]):
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Décoder le sujet
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    
                    # Décoder l'expéditeur
                    from_, encoding = decode_header(msg["From"])[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding or "utf-8", errors="ignore")
                    
                    # Récupérer le corps du message
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    messages_liste.append({
                        "from": from_,
                        "subject": subject,
                        "body": body[:150] + "..." if len(body) > 150 else body
                    })
        mail.logout()
    except Exception as e:
        messages_liste.append({"from": "Système", "subject": "Erreur", "body": f"Erreur de connexion : {e}"})
    
    return messages_liste

# CODE HTML INTÉGRÉ DIRECTEMENT
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon Invite de Messages</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
        .chat-container { max-width: 800px; margin: 50px auto; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
        .chat-header { background-color: #007bff; color: white; padding: 20px; font-size: 1.25rem; font-weight: bold; }
        .message-box { padding: 20px; max-height: 600px; overflow-y: auto; }
        .message-card { background-color: #f1f0f0; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #007bff; }
        .message-sender { font-weight: bold; color: #333; font-size: 0.9rem; }
        .message-subject { font-style: italic; color: #555; margin-bottom: 5px; }
        .message-body { font-size: 0.95rem; color: #444; white-space: pre-line; }
    </style>
</head>
<body>
<div class="container">
    <div class="chat-container">
        <div class="chat-header d-flex justify-content-between align-items-center">
            <span>📥 Invite de Messages Récents</span>
            <button class="btn btn-sm btn-light" onclick="window.location.reload();">Actualiser</button>
        </div>
        <div class="message-box">
            {% for email in emails %}
            <div class="message-card">
                <div class="message-sender">De : {{ email.from }}</div>
                <div class="message-subject">Sujet : {{ email.subject }}</div>
                <hr class="my-2">
                <div class="message-body">{{ email.body }}</div>
            </div>
            {% else %}
            <div class="text-center text-muted">Aucun message trouvé ou erreur de connexion.</div>
            {% endfor %}
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    emails = recuperer_messages()
    return render_template_string(HTML_TEMPLATE, emails=emails)

if __name__ == '__main__':
    # Idéal pour l'exécution locale ou le déploiement de base
    app.run(host='0.0.0.0', port=5000, debug=True)
