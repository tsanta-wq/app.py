from flask import Flask, render_template_string

app = Flask(__name__)

# CONFIGURATION DE TON COMPTE FACEBOOK
FACEBOOK_PSEUDO = "Tsantaniaina.Loup"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contactez Tsanta</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
        .form-container { max-width: 500px; margin: 80px auto; background: white; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); overflow: hidden; }
        .form-header { background-color: #0084FF; color: white; padding: 25px; font-size: 1.4rem; font-weight: bold; }
        .form-body { padding: 30px; }
        .btn-messenger { background-color: #0084FF; color: white; width: 100%; border-radius: 8px; padding: 12px; font-weight: bold; font-size: 1.1rem; text-decoration: none; display: inline-block; transition: background 0.2s; }
        .btn-messenger:hover { background-color: #0066cc; color: white; }
        .info-text { color: #65676B; font-size: 0.9rem; margin-bottom: 25px; }
    </style>
</head>
<body>
<div class="container">
    <div class="form-container">
        <div class="form-header text-center">
            💬 Discuter avec Tsanta
        </div>
        <div class="form-body text-center">
            <p class="info-text">
                Pour m'envoyer un message, cliquez sur le bouton ci-dessous. 
                Une discussion privée s'ouvrira directement sur votre application Messenger.
            </p>
            
            <a href="https://m.me/{{ pseudo }}" target="_blank" class="btn-messenger">
                Ouvrir Facebook Messenger 🚀
            </a>
        </div>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, pseudo=FACEBOOK_PSEUDO)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
