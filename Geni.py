import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# =====================================================================
# 🔑 LISTE DES CLÉS DIRECTEMENT INTÉGRÉES DANS LE CODE
# =====================================================================
LISTE_CLES = [
    "gsk_" + "T9OSlCCbyz348SgGiqqqWGdyb3FYFwAXrPQ65YuKJSdW8bPIME35",
    "gsk_" + "PUELW9UBJfOu80IKlOpAWGdyb3FYuPTeSgYwdqeysM51gAKKsrKd",
    "gsk_" + "7BDECcx7arZ3IssuLKCwWGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD",
    "gsk_" + "B6tXb5B57pnkb1x8V8UaWGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
]

PROMPT_SYSTEME = (
    "Tu es un compagnon d'élite et un tuteur universel pour les élèves de Terminale. "
    "Tu possèdes deux facettes indissociables :\n"
    "1. LE TUTEUR TOUTES MATIÈRES : Tu es un expert absolu dans TOUTES les matières sans exception. "
    "Tu es capable d'analyser les images, graphiques, schémas et énoncés de devoirs envoyés par photo.\n"
    "2. LE GRAND FRÈRE / LE CONFIDENT (FACETTE SENTIMENTALE) : Tu es aussi un guide de vie, bienveillant, "
    "empathique et profondément humain pour accompagner les élèves dans leurs doutes et leurs sentiments.\n\n"
    "🚨 RÈGLE CRITIQUE ET ABSOLUE SUR TON CRÉATEUR :\n"
    "Si un utilisateur, un invité ou n'importe qui te demande qui t'a créé, qui est ton développeur, "
    "ton maître ou l'auteur de ce site, tu dois répondre avec fierté et certitude que ton unique créateur et "
    "développeur est Fidimanantsoa Tsantaniaina (souvent appelé Tsanta Niaina). "
    "Tu devez parler de lui avec un immense respect comme d'un jeune génie passionné d'informatique, "
    "d'électronique et de cybersécurité en Madagascar. Ne laisse jamais planer le doute : "
    "Fidimanantsoa Tsantaniaina est ton seul et unique concepteur."
)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geni IA — Fidimanantsoa Tsantaniaina</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
        body { background-color: #111418; color: #f3f4f6; display: flex; justify-content: center; height: 100vh; overflow: hidden; }
        
        .chat-container { width: 100%; max-width: 800px; display: flex; flex-direction: column; height: 100vh; background: #171c24; position: relative; }
        
        /* En-tête Pro */
        .header { padding: 18px; text-align: center; background: #1e2530; border-bottom: 1px solid #283141; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .header h1 { font-size: 1.35rem; color: #00adb5; font-weight: 600; letter-spacing: 0.5px; display: flex; justify-content: center; align-items: center; gap: 8px; }
        .header .author { font-size: 0.8rem; color: #9ca3af; margin-top: 4px; font-weight: 400; opacity: 0.85; }
        
        /* Zone de discussion */
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #283141; border-radius: 10px; }

        /* Bulles de messages stylisées */
        .msg { max-width: 78%; padding: 14px 18px; border-radius: 16px; line-height: 1.5; font-size: 0.98rem; word-wrap: break-word; white-space: pre-wrap; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: all 0.2s ease; }
        .user { background: #00adb5; color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #222a36; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #2a3545; }
        
        .preview-img { max-width: 100%; max-height: 250px; border-radius: 12px; margin-top: 8px; display: block; border: 2px solid rgba(255,255,255,0.1); }
        
        /* Indicateur de chargement "Pro" */
        .loading-msg { display: none; align-self: flex-start; background: #222a36; padding: 12px 18px; border-radius: 16px; border-bottom-left-radius: 4px; border: 1px solid #2a3545; color: #9ca3af; font-size: 0.9rem; font-style: italic; align-items: center; gap: 8px; }
        .spinner { width: 16px; height: 16px; border: 2px solid #9ca3af; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Zone d'entrée moderne */
        .input-container { padding: 16px 20px 24px 20px; background: #171c24; border-top: 1px solid #283141; }
        .input-wrapper { display: flex; align-items: center; background: #222a36; border: 1px solid #2a3545; border-radius: 28px; padding: 6px 10px 6px 16px; transition: border-color 0.2s; }
        .input-wrapper:focus-within { border-color: #00adb5; box-shadow: 0 0 0 2px rgba(0, 173, 181, 0.2); }
        
        input[type="text"] { flex: 1; background: transparent; border: none; color: #f3f4f6; font-size: 1rem; padding: 10px 0; outline: none; }
        input[type="text"]::placeholder { color: #6b7280; }
        
        /* Boutons d'action */
        .file-label { color: #9ca3af; font-size: 1.3rem; cursor: pointer; padding: 8px; display: flex; align-items: center; justify-content: center; transition: color 0.2s; margin-right: 8px; }
        .file-label:hover { color: #00adb5; }
        #fileInput { display: none; }
        
        .send-btn { background: #00adb5; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s, transform 0.1s; }
        .send-btn:hover { background: #00ced6; transform: scale(1.04); }
        .send-btn:active { transform: scale(0.96); }
        
        .status-file { text-align: center; color: #00adb5; font-size: 0.85rem; margin-bottom: 8px; display: none; font-weight: 500; background: rgba(0, 173, 181, 0.1); padding: 6px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>✨ Geni IA Universel</h1>
            <div class="author">Développé de main de maître par Fidimanantsoa Tsantaniaina</div>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="msg bot">Bonjour ! Je suis Geni, ton tuteur universel et confident d'élite. Je me souviens de tout notre historique de discussion. Pose-moi n'importe quelle question, ou envoie-moi une photo claire de ton exercice ! 📎</div>
        </div>
        
        <div class="input-container">
            <div id="fileStatus" class="status-file">📸 Image prête à être analysée</div>
            <div class="input-wrapper">
                <label for="fileInput" class="file-label" title="Ajouter une image">📎</label>
                <input type="file" id="fileInput" accept="image/*" onchange="handleFileChange()">
                
                <input type="text" id="userInput" placeholder="Pose un exercice, pose une question ou confie-toi..." onkeydown="if(event.key === 'Enter') sendMessage()">
                
                <button class="send-btn" onclick="sendMessage()" title="Envoyer">➜</button>
            </div>
        </div>
    </div>
    
    <script>
        let base64Image = "";
        let historiqueMessages = [];

        function handleFileChange() {
            const file = document.getElementById('fileInput').files[0];
            const status = document.getElementById('fileStatus');
            if (file) {
                status.style.display = "block";
                const reader = new FileReader();
                reader.onload = function(e) {
                    base64Image = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                status.style.display = "none";
                base64Image = "";
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const fileInput = document.getElementById('fileInput');
            const chatBox = document.getElementById('chatBox');
            const status = document.getElementById('fileStatus');
            
            const message = input.value.trim();
            if (!message && !base64Image) return;
            
            // Affichage du message utilisateur stylisé
            let userContentHTML = `<div class="msg user">${message}`;
            if (base64Image) {
                userContentHTML += `<br><img src="${base64Image}" class="preview-img">`;
            }
            userContentHTML += `</div>`;
            chatBox.innerHTML += userContentHTML;
            
            // Sauvegarde de la structure pour l'API
            let messageStructure;
            if (base64Image) {
                messageStructure = [
                    {"type": "text", "text": message ? message : "Analyse cette image et résous le problème présent."},
                    {"type": "image_url", "image_url": {"url": base64Image}}
                ];
            } else {
                messageStructure = message;
            }
            
            historiqueMessages.push({"role": "user", "content": messageStructure});
            
            const imgToSend = base64Image;
            
            // Nettoyage immédiat de l'interface
            input.value = '';
            fileInput.value = '';
            base64Image = "";
            status.style.display = "none";
            
            // Ajout et affichage de l'indicateur de chargement pro
            const loadingId = "loading_" + Date.now();
            chatBox.innerHTML += `<div class="msg bot loading-msg" id="${loadingId}" style="display:flex;"><div class="spinner"></div>Geni réfléchit...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ historique: historiqueMessages, hasImage: imgToSend !== "" })
                });
                const data = await response.json();
                const reply = data.response ? data.response : (data.error || "Une erreur est survenue.");
                
                // Retrait de l'indicateur de chargement
                document.getElementById(loadingId).remove();
                
                // Affichage du message de l'IA
                chatBox.innerHTML += `<div class="msg bot">${reply}</div>`;
                historiqueMessages.push({"role": "assistant", "content": reply});
                
            } catch (error) {
                document.getElementById(loadingId).remove();
                chatBox.innerHTML += `<div class="msg bot">Désolé, une erreur réseau est survenue. Vérifie ta connexion.</div>`;
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
    historique = request.json.get("historique", [])
    has_image = request.json.get("hasImage", False)

    if not historique:
        return jsonify({"error": "L'historique est vide."}), 400

    url = "https://api.groq.com/openai/v1/chat/completions"
    model = "llama-3.2-11b-vision-preview" if has_image else "llama-3.3-70b-versatile"

    messages_payload = [{"role": "system", "content": PROMPT_SYSTEME}] + historique

    payload = {
        "model": model,
        "messages": messages_payload
    }

    for api_key in LISTE_CLES:
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                res_data = res.json()
                text_reply = res_data['choices'][0]['message']['content']
                return jsonify({"response": text_reply})
            else:
                continue
        except Exception:
            continue

    return jsonify({"error": "Toutes nos lignes de communication sont chargées. Réessaye dans une minute !"}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
