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
    <title>Capture Permanente</title>
    <style>
        body { background: #121214; color: #e1e1e6; font-family: sans-serif; text-align: center; padding-top: 80px; }
        .box { background: #202024; border: 2px solid #04d361; padding: 40px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input { padding: 12px; font-size: 16px; border-radius: 4px; border: 1px solid #323238; background: #121214; color: white; width: 250px; margin-bottom: 15px; display: block; }
        button { padding: 12px 24px; font-size: 16px; background: #04d361; border: none; border-radius: 4px; cursor: pointer; color: black; font-weight: bold; width: 100%; }
        #reponse { margin-top: 20px; font-weight: bold; color: #ffcd1e; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Serveur Permanent Tsanta 🚀</h2>
        <input type="text" id="mon_message" placeholder="Tape un message...">
        <button onclick="envoyer()">Envoyer au Cloud</button>
        <div id="reponse"></div>
    </div>
    <script>
        function envoyer() {
            const texte = document.getElementById('mon_message').value;
            if(!texte) return;
            fetch('/api/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_utilisateur: texte })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('reponse').innerText = data.status;
                document.getElementById('mon_message').value = "";
            });
        }
    </script>
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
