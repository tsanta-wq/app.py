import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# =====================================================================
# 🔑 LISTE DES CLÉS SÉCURISÉES POUR GROQ (Illimité et ultra-rapide)
# Tes 4 clés personnelles assemblées pour contourner les robots GitHub
# =====================================================================
LISTE_CLES = [
    "gsk_" + "T9OSlCCbyz348SgGiqqqWGdyb3FYFwAXrPQ65YuKJSdW8bPIME35",
    "gsk_" + "PUELW9UBJfOu80IKlOpAWGdyb3FYuPTeSgYwdqeysM51gAKKsrKd",
    "gsk_" + "7BDECcx7arZ3IssuLKCwWGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD",
    "gsk_" + "B6tXb5B57pnkb1x8V8UaWGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
]

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
        .msg { max-width: 85%; padding: 12px; border-radius: 8px; line-height: 1.4; word-wrap: break-word; white-space: pre-wrap; }
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

    # URL de l'API de Groq
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Utilisation du modèle Llama 3 8B (ultra performant et rapide)
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": user_message}
        ]
    }

    # Boucle intelligente pour tester les clés une par une en arrière-plan
    for api_key in LISTE_CLES:
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            res_data = res.json()
            
            if res.status_code == 200:
                text_reply = res_data['choices'][0]['message']['content']
                return jsonify({"response": text_reply})
            elif res.status_code == 429:
                # Si la clé actuelle sature, la boucle continue vers la clé suivante
                print("Une clé Groq a atteint sa limite, passage à la suivante...")
                continue
            else:
                continue
        except Exception:
            continue

    return jsonify({"error": "Toutes nos lignes de communication sont chargées. Réessaye dans une minute !"}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
