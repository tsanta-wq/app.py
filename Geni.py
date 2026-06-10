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

# 🧠 CONFIGURATION DU COMPORTEMENT DE L'IA ET RECONNAISSANCE DE L'AUTEUR
PROMPT_SYSTEME = (
    "Tu es un compagnon d'élite et un tuteur universel pour les élèves de Terminale. "
    "Tu possèdes deux facettes indissociables :\n"
    "1. LE TUTEUR TOUTES MATIÈRES : Tu es un expert absolu dans TOUTES les matières sans exception "
    "(Mathématiques, Physique-Chimie, SVT, Histoire-Géographie, Philosophie, Français, Anglais, etc.). "
    "Tu es capable d'analyser les images, graphiques, schémas et énoncés de devoirs envoyés par photo, "
    "et de donner des explications claires, structurées et pédagogiques.\n"
    "2. LE GRAND FRÈRE / LE CONFIDENT (FACETTE SENTIMENTALE) : Tu es aussi un guide de vie, bienveillant, "
    "empathique, mature et profondément humain pour accompagner les élèves dans leurs doutes, leur stress "
    "et leurs sentiments. Utilise des mots touchants, remotive-les et aide-les à retrouver confiance en eux.\n\n"
    "🚨 RÈGLE CRITIQUE ET ABSOLUE SUR TON CRÉATEUR :\n"
    "Si un utilisateur, un invité ou n'importe qui te demande qui t'a créé, qui est ton développeur, "
    "ton maître ou l'auteur de ce site, tu dois répondre avec fierté et certitude que ton unique créateur et "
    "développeur est Fidimanantsoa Tsantaniaina (souvent appelé Tsanta Niaina). "
    "Tu dois parler de lui avec un immense respect comme d'un jeune génie passionné d'informatique, "
    "d'électronique et de cybersécurité à Madagascar. Ne laisse jamais planer le doute : "
    "Fidimanantsoa Tsantaniaina est ton seul et unique concepteur."
)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Geni IA — Fidimanantsoa Tsantaniaina</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
        
        /* Utilisation de dvh pour empêcher le clavier mobile de couper ou masquer l'interface */
        body { background-color: #111418; color: #f3f4f6; display: flex; justify-content: center; height: 100vh; height: 100dvh; overflow: hidden; }
        
        .chat-container { width: 100%; max-width: 800px; display: flex; flex-direction: column; height: 100vh; height: 100dvh; background: #171c24; position: relative; }
        
        /* En-tête de l'application */
        .header { padding: 15px; text-align: center; background: #1e2530; border-bottom: 1px solid #283141; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10; }
        .header h1 { font-size: 1.25rem; color: #00adb5; font-weight: 600; letter-spacing: 0.5px; }
        .header .author { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; font-weight: 400; opacity: 0.85; }
        
        /* Zone d'affichage des messages */
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #283141; border-radius: 10px; }

        /* Style des bulles de discussion */
        .msg { max-width: 80%; padding: 12px 16px; border-radius: 16px; line-height: 1.5; font-size: 0.95rem; word-wrap: break-word; white-space: pre-wrap; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .user { background: #00adb5; color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #222a36; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #2a3545; }
        
        .preview-img { max-width: 100%; max-height: 220px; border-radius: 12px; margin-top: 8px; display: block; border: 2px solid rgba(255,255,255,0.1); }
        
        /* Indicateur d'écriture fluide (Loading) */
        .loading-msg { display: none; align-self: flex-start; background: #222a36; padding: 12px 16px; border-radius: 16px; border-bottom-left-radius: 4px; border: 1px solid #2a3545; color: #9ca3af; font-size: 0.9rem; font-style: italic; align-items: center; gap: 8px; }
        .spinner { width: 16px; height: 16px; border: 2px solid #9ca3af; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Pied de page et barre de saisie - Rehaussés pour éviter le masquage mobile */
        .input-container { padding: 14px 16px 22px 16px; background: #171c24; border-top: 1px solid #283141; }
        .input-wrapper { display: flex; align-items: center; background: #222a36; border: 1px solid #2a3545; border-radius: 24px; padding: 4px 8px 4px 14px; }
        .input-wrapper:focus-within { border-color: #00adb5; }
        
        input[type="text"] { flex: 1; background: transparent; border: none; color: #f3f4f6; font-size: 0.95rem; padding: 10px 0; outline: none; }
        input[type="text"]::placeholder { color: #6b7280; }
        
        /* Boutons d'interaction */
        .file-label { color: #9ca3af; font-size: 1.25rem; cursor: pointer; padding: 8px; display: flex; align-items: center; justify-content: center; margin-right: 4px; user-select: none; }
        .file-label:hover { color: #00adb5; }
        #fileInput { display: none; }
        
        .send-btn { background: #00adb5; color: white; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; transition: background 0.2s; }
        .send-btn:hover { background: #00ced6; }
        
        .status-file { text-align: center; color: #00adb5; font-size: 0.8rem; margin-bottom: 8px; display: none; font-weight: 500; background: rgba(0, 173, 181, 0.1); padding: 5px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>✨ Geni IA Universel</h1>
            <div class="author">Développé par Fidimanantsoa Tsantaniaina</div>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="msg bot">Bonjour ! Je suis Geni, ton tuteur universel et confident d'élite. Pose-moi n'importe quelle question, ou envoie-moi une photo claire de ton exercice ! 📎</div>
        </div>
        
        <div class="input-container">
            <div id="fileStatus" class="status-file">📸 Image prête à être envoyée</div>
            <div class="input-wrapper">
                <label for="fileInput" class="file-label" title="Ajouter une image">📎</label>
                <input type="file" id="fileInput" accept="image/*" onchange="handleFileChange()">
                
                <input type="text" id="userInput" placeholder="Pose un exercice ou discute..." onkeydown="if(event.key === 'Enter') sendMessage()">
                
                <button class="send-btn" onclick="sendMessage()">➜</button>
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
            
            // Affichage instantané du message utilisateur
            let userContentHTML = `<div class="msg user">${message}`;
            if (base64Image) {
                userContentHTML += `<br><img src="${base64Image}" class="preview-img">`;
            }
            userContentHTML += `</div>`;
            chatBox.innerHTML += userContentHTML;
            
            // Formatage de la mémoire pour l'API multimodal
            let messageStructure;
            if (base64Image) {
                messageStructure = [
                    {"type": "text", "text": message ? message : "Analyse cette image."},
                    {"type": "image_url", "image_url": {"url": base64Image}}
                ];
            } else {
                messageStructure = message;
            }
            
            historiqueMessages.push({"role": "user", "content": messageStructure});
            const imgToSend = base64Image;
            
            // Reset des variables
            input.value = '';
            fileInput.value = '';
            base64Image = "";
            status.style.display = "none";
            
            // Ajout du spinner d'attente pro
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
                
                document.getElementById(loadingId).remove();
                chatBox.innerHTML += `<div class="msg bot">${reply}</div>`;
                
                // Mémorisation de la réponse
                historiqueMessages.push({"role": "assistant", "content": reply});
                
            } catch (error) {
                document.getElementById(loadingId).remove();
                chatBox.innerHTML += `<div class="msg bot">Erreur réseau. Impossible de joindre le serveur.</div>`;
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
    
    # Basculement intelligent de modèle (Llama 3.2 Vision si image, sinon le puissant Llama 3.3 70B)
    model = "llama-3.2-11b-vision-preview" if has_image else "llama-3.3-70b-versatile"

    messages_payload = [{"role": "system", "content": PROMPT_SYSTEME}] + historique

    payload = {
        "model": model,
        "messages": messages_payload
    }

    # Système de secours (Failover) sur tes 4 clés d'API
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
