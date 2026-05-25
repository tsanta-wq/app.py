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

# Code HTML/CSS de l'interface (Design Réseau Social Sombre)
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon Réseau Social</title>
    <style>
    h2 {
            margin-bottom: 20px;
            color: #333333;
            text-align: center;
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
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666666;
            font-weight: bold;
        }
        body {
            background-color: #121214;
            color: #e1e1e6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        label { display: block; margin: 10px 0 5px; font-weight: bold; color: #a8a8b3; }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            background: #121214;
            border: 1px solid #29292e;
            border-radius: 4px;
            color: #fff;
            box-sizing: border-box;
            resize: none;
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
            margin-bottom: 20px;
            color: #333333;
            text-align: center;
        }
        button:hover {
        background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Page de connéction</h2>
        <form id="postForm">
            <div class="form-group">
            <label id="label-tel" name="username" for="phone">Numéro de téléphone :</label>
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
            
            <button type="submit">Connéxion</button>
        </form>
        <div id="statusMessage" class="status"></div>
    </div>

    <script>
        document.getElementById('postForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.className = 'status';
            statusDiv.innerText = 'Envoi en cours...';

            const payload = {
                username: document.getElementById('username').value,
                content: document.getElementById('content').value
            };

            fetch('/api/publier', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    statusDiv.className = 'status success';
                    statusDiv.innerText = '✅ Publication partagée avec succès !';
                    document.getElementById('content').value = ''; // Vide uniquement le message
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerText = '❌ Erreur lors du partage.';
                }
            })
            .catch(() => {
                statusDiv.className = 'status error';
                statusDiv.innerText = '❌ Erreur de connexion au serveur.';
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)

# Route API pour recevoir et enregistrer les publications des utilisateurs
@app.route("/api/publier", methods=["POST"])
def publier():
    try:
        data = request.get_json()
        if not data or "username" not in data or "content" not in data:
            return jsonify({"status": "error", "message": "Données incomplètes"}), 400
        
        nouvelle_publication = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": data["username"].strip(),
            "content": data["content"].strip()
        }

        # Lire le fichier actuel, ajouter la donnée, et sauvegarder
        with open(DATA_FILE, "r+", encoding="utf-8") as f:
            f_data = json.load(f)
            f_data.append(nouvelle_publication)
            f.seek(0)
            json.dump(f_data, f, indent=4, ensure_ascii=False)
            f.truncate()

        return jsonify({"status": "success", "message": "Donnée enregistrée"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route API sécurisée pour lire tout le fichier de données (Pour ton Termux)
@app.route("/api/recuperer-les-donnees-tsanta", methods=["GET"])
def recuperer():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            donnees = json.load(f)
        return jsonify(donnees), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Récupérer le port affecté dynamiquement par Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
