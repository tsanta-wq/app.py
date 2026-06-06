import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Colle ta clé complète commençant par AQ ici
GOOGLE_API_KEY = "AQ.Ab8RN6JHOyti5g4wWVJKM3qzhzuIYm4eGEmrUt5Qu1P3uoQSJQ"

PROMPT_SYSTEME = (
    "Tu es une intelligence artificielle d'élite, experte pour accompagner les élèves de Terminale. "
    "Tes spécialités absolues sont : l'Histoire-Géographie, les Mathématiques, la Physique-Chimie et l'Anglais. "
    "Tu t'adaptes parfaitement au niveau des lycéens. Tes explications doivent être claires, structurées, "
    "rigoureuses et très pédagogiques. "
    "Si un utilisateur te pose une question totalement hors de ces matières, rappelle-lui gentiment tes domaines de spécialité."
)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Terminale - Tsanta Niaina</title>
    <style>
        * { box-sizing: border-box; }
        body { background-color: #121212; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 10px; }
        .chat-container { max-width: 600px; margin: auto; display: flex; flex-direction: column; height: 95vh; }
        .header { text-align: center; color: #00adb5; margin: 10px 0 5px 0; font-size: 1.5rem; font-weight: bold; }
        .author { text-align: center; color: #888888; font-size: 0.9rem; margin-bottom: 15px; font-style: italic; }
        .chat-box { flex: 1; border: 1px solid #2d2d2d; padding: 15px; overflow-y: auto; background: #1e1e1e; border-radius: 8px; display: flex; flex-direction: column; gap: 10px; }
        .input-area { display: flex; margin-top: 10px; gap: 5px; }
        input { flex: 1; padding: 14px; background: #2d2d2d; border: 1px solid #3d3d3d; color: white; border-radius: 6px; font-size: 1rem; }
        input:focus { outline: 1px solid #00adb5; }
        button { background: #00adb5; color: white; border: none; padding: 14px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 1rem; }
        button:active { opacity: 0.8; }
        .msg { max-width: 85%; padding: 12px; border-radius: 8px; line-height: 1.4; word-wrap: break-word; }
        .user { background: #00adb5; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot { background: #2d2d2d; color: #e0e0e0; align-self: flex-start; border-bottom-left-radius: 2px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">🎓 Code Tuteur IA — Terminale</div>
        <div class="author">Créé par Tsanta Niaina</div>
        <div class="chat-box" id="chatBox">
            <div class="msg bot">Salut ! Je suis ton IA de révision. Pose-moi une question en Histoire-Géo, Maths, Physique ou Anglais !</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Pose ton exercice ou ta question..." onkeydown="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Envoyer</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            if (!message) return;
            chatBox.innerHTML += `<div class="msg user">${message}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                const reply = data.response ? data.response : (data.error || "Une erreur est survenue.");
                chatBox.innerHTML += `<div class="msg bot">${reply}</div>`;
            } catch (error) {
                chatBox.innerHTML += `<div class="msg bot">Erreur réseau.</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Le message est vide."}), 400
    
    # Appel HTTP direct à l'API de Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY.strip()}"
    
    message_complet = f"{PROMPT_SYSTEME}\n\nL'élève demande : {user_message}"
    payload = {
        "contents": [{
            "parts": [{"text": message_complet}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        res_data = res.json()
        
        if res.status_code == 200:
            text_reply = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"response": text_reply})
        else:
            return jsonify({"error": f"Erreur API Google ({res.status_code}) : {res.text}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
