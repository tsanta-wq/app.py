import os
from flask import Flask, render_template_string

app = Flask(__name__)

# CONFIGURATION DE L'INTERFACE AIxl (100% Textuelle - Anti-bug)
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AIxl — Fidimanantsoa Tsantaniaina</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
        body { background-color: #111418; color: #f3f4f6; display: flex; justify-content: center; height: 100vh; height: 100dvh; overflow: hidden; }
        .chat-container { width: 100%; max-width: 800px; display: flex; flex-direction: column; height: 100vh; height: 100dvh; background: #171c24; position: relative; }
        .header { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; background: #1e2530; border-bottom: 1px solid #283141; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10; }
        .header-titles { text-align: left; }
        .header h1 { font-size: 1.35rem; color: #00adb5; font-weight: 700; letter-spacing: 0.8px; }
        .header .author { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; font-weight: 400; opacity: 0.85; }
        .clear-btn { background: transparent; border: 1px solid #3a475e; color: #9ca3af; padding: 8px 14px; border-radius: 20px; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; gap: 6px; transition: all 0.2s; user-select: none; font-weight: 500; }
        .clear-btn:hover { background: #e63946; color: white; border-color: #e63946; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #283141; border-radius: 10px; }
        .msg { max-width: 85%; padding: 12px 16px; border-radius: 16px; line-height: 1.5; font-size: 0.95rem; word-wrap: break-word; white-space: pre-wrap; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .user { background: #00adb5; color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #222a36; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #2a3545; }
        .loading-msg { display: none; align-self: flex-start; background: #222a36; padding: 12px 16px; border-radius: 16px; border-bottom-left-radius: 4px; border: 1px solid #2a3545; color: #9ca3af; font-size: 0.9rem; font-style: italic; align-items: center; gap: 8px; }
        .spinner { width: 16px; height: 16px; border: 2px solid #9ca3af; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .input-container { padding: 14px 16px 22px 16px; background: #171c24; border-top: 1px solid #283141; }
        .input-wrapper { display: flex; align-items: center; background: #222a36; border: 1px solid #2a3545; border-radius: 24px; padding: 4px 8px 4px 14px; }
        .input-wrapper:focus-within { border-color: #00adb5; }
        input[type="text"] { flex: 1; background: transparent; border: none; color: #f3f4f6; font-size: 0.95rem; padding: 10px 0; outline: none; }
        input[type="text"]::placeholder { color: #6b7280; }
        .send-btn { background: #00adb5; color: white; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; transition: background 0.2s; }
        .send-btn:hover { background: #00ced6; }
        .error-details { background: #3d1e22; color: #ffb3b3; border: 1px solid #e63946; padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div class="header-titles">
                <h1>⚡ AIxl</h1>
                <div class="author">Développé par Fidimanantsoa Tsantaniaina</div>
            </div>
            <button class="clear-btn" onclick="reinitialiserDiscussion()">🗑️ Effacer</button>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Pose ta question ici..." onkeydown="if(event.key === 'Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">➜</button>
            </div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];

        // Clés API scindées de Groq (Rotation automatique sur 8 clés sécurisées)
        const PARTIE_A = [
            "gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue",
            "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"
        ];

        const PARTIE_B = [
            "WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq",
            "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
        ];

        const LISTE_CLES = PARTIE_A.map((partie, index) => partie + PARTIE_B[index]);

        const PROMPT_SYSTEME = "Tu es AIxl, un tuteur d'élite universel et un confident pour les étudiants. Ton développeur et créateur unique est Fidimanantsoa Tsantaniaina. Tu es une IA 100% textuelle : tu es incapable de voir, recevoir, traiter ou analyser des images ou des fichiers. Si on te parle d'une image, rappelle poliment que tu es uniquement textuel.";

        // LE SCRIPT WINDOW.ONLOAD SÉCURISÉ EST ICI :
        window.onload = function() {
            const chatBox = document.getElementById('chatBox');
            try {
                // Utilisation d'un espace mémoire isolé pour AIxl pour éviter tout conflit de cache
                const historiqueSauvegarde = localStorage.getItem('aixl_chat_history');
                
                if (historiqueSauvegarde) {
                    historiqueMessages = JSON.parse(historiqueSauvegarde);
                    historiqueMessages.forEach((msg) => {
                        if (msg.role === "user") {
                            chatBox.innerHTML += `<div class="msg user">${msg.content}</div>`;
                        } else if (msg.role === "assistant") {
                            chatBox.innerHTML += `<div class="msg bot">${msg.content}</div>`;
                        }
                    });
                } else {
                    chatBox.innerHTML = `<div class="msg bot">Bonjour ! Je suis <b>AIxl</b>, ton compagnon IA entièrement textuel. En quoi puis-je t'aider aujourd'hui ? ⚡</div>`;
                }
            } catch (e) {
                chatBox.innerHTML = `<div class="msg bot">Bonjour ! Je suis <b>AIxl</b>. Pose-moi tes questions ! ⚡</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        };

        function reinitialiserDiscussion() {
            try {
                localStorage.removeItem('aixl_chat_history');
                historiqueMessages = [];
                document.getElementById('chatBox').innerHTML = `<div class="msg bot">Discussion réinitialisée ! ⚡</div>`;
            } catch(e) {
                location.reload();
            }
        }

        async function appelerGroqDirect(payload) {
            const url = "https://api.groq.com/openai/v1/chat/completions";
            let rapportErreures = "";

            for (let i = 0; i < LISTE_CLES.length; i++) {
                let key = LISTE_CLES[i];
                try {
                    const response = await fetch(url, {
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${key.trim()}`,
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(payload)
                    });

                    if (response.status === 200) {
                        const resData = await response.json();
                        return { succes: true, data: resData.choices[0].message.content };
                    } else {
                        const textErreur = await response.text();
                        rapportErreures += `• Clé ${i+1} (Limite atteinte ou indisponible)\\n`;
                    }
                } catch (e) {
                    rapportErreures += `• Clé ${i+1} (Erreur Connexion)\\n`;
                }
            }
            return { succes: false, erreurTexte: rapportErreures };
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            if (!message) return;

            chatBox.innerHTML += `<div class="msg user">${message}</div>`;
            historiqueMessages.push({"role": "user", "content": message});

            input.value = '';
            
            const loadingId = "loading_" + Date.now();
            chatBox.innerHTML += `<div class="msg bot loading-msg" id="${loadingId}" style="display:flex;"><div class="spinner"></div>AIxl réfléchit...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            const payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages]
            };

            const resultat = await appelerGroqDirect(payload);
            
            if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();

            if (resultat.succes) {
                chatBox.innerHTML += `<div class="msg bot">${resultat.data}</div>`;
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
                localStorage.setItem('aixl_chat_history', JSON.stringify(historiqueMessages));
            } else {
                chatBox.innerHTML += `
                    <div class="msg bot">
                        ❌ <b>Toutes les clés sont saturées</b><br>
                        Le quota maximum de requêtes par minute a été atteint. Patiente 1 à 2 minutes sans envoyer de message, puis réessaye !
                    </div>`;
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
