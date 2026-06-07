import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Le prompt système reste le même pour guider l'IA locale
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
        .author { text-align: center; color: #888888; font-size: 0.9rem; margin-bottom: 10px; font-style: italic; }
        
        /* Barre de statut du chargement de l'IA */
        .status-container { background: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px dashed #00adb5; margin-bottom: 10px; font-size: 0.9rem; text-align: center; }
        .progress-bar { width: 0%; height: 6px; background: #00adb5; margin-top: 8px; border-radius: 3px; transition: width 0.3s; }
        
        .chat-box { flex: 1; border: 1px solid #2d2d2d; padding: 15px; overflow-y: auto; background: #1e1e1e; border-radius: 8px; display: flex; flex-direction: column; gap: 10px; }
        .input-area { display: flex; margin-top: 10px; gap: 5px; }
        input { flex: 1; padding: 14px; background: #2d2d2d; border: 1px solid #3d3d3d; color: white; border-radius: 6px; font-size: 1rem; }
        input:focus { outline: 1px solid #00adb5; }
        button { background: #00adb5; color: white; border: none; padding: 14px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 1rem; }
        button:disabled { background: #444; cursor: not-allowed; }
        button:active { opacity: 0.8; }
        .msg { max-width: 85%; padding: 12px; border-radius: 8px; line-height: 1.4; word-wrap: break-word; white-space: pre-wrap; }
        .user { background: #00adb5; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot { background: #2d2d2d; color: #e0e0e0; align-self: flex-start; border-bottom-left-radius: 2px; }
    </style>
    
    <!-- Chargement du module WebLLM pour faire tourner l'IA dans le navigateur -->
    <script type="module">
        import * as webllm from "https://esm.run/@mlc-ai/web-llm";
        
        // On choisit "Llama-3-8B-Instruct-q4f16_1-MLC" ou "Gemma-2b-it-q4f16_1-MLC" (très léger pour les téléphones)
        const selectedModel = "Gemma-2b-it-q4f16_1-MLC";
        let engine;

        async function init() {
            const statusText = document.getElementById("statusText");
            const progressBar = document.getElementById("progressBar");
            const sendBtn = document.getElementById("sendBtn");
            
            try {
                engine = await webllm.CreateEngine(selectedModel, {
                    initProgressCallback: (report) => {
                        statusText.innerText = report.text;
                        // Extrait le pourcentage si présent dans le texte de chargement
                        if (report.text.includes("%")) {
                            const match = report.text.match(/(\d+)%/);
                            if (match) progressBar.style.width = match[1] + "%";
                        } else {
                            progressBar.style.width = "50%";
                        }
                    }
                });
                statusText.innerHTML = "✨ L'IA est prête ! Elle s'exécute sur ton appareil de manière illimitée.";
                progressBar.style.width = "100%";
                progressBar.style.background = "#28a745";
                sendBtn.disabled = false;
            } catch (err) {
                statusText.innerHTML = "❌ Erreur de chargement (Ton navigateur/appareil ne supporte pas WebGPU).";
                console.error(err);
            }
        }

        window.sendMessage = async function() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            if (!message || !engine) return;
            
            chatBox.innerHTML += `<div class="msg user">${message}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Création de l'animation de chargement pour le bot
            const botMsgId = "bot-" + Date.now();
            chatBox.innerHTML += `<div class="msg bot" id="${botMsgId}">En train de réfléchir...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                const promptSysteme = document.getElementById("promptSysteme").value;
                const messages = [
                    { role: "system", content: promptSysteme },
                    { role: "user", content: message }
                ];
                
                const reply = await engine.chat.completions.create({ messages });
                const textReply = reply.choices[0].message.content;
                
                document.getElementById(botMsgId).innerText = textReply;
            } catch (error) {
                document.getElementById(botMsgId).innerText = "Une erreur est survenue lors de la génération locale.";
                console.error(error);
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // Lance le chargement dès l'ouverture de la page
        window.addEventListener("DOMContentLoaded", init);
    </script>
</head>
<body>
    <!-- Champ caché pour transmettre le prompt système au script JS -->
    <input type="hidden" id="promptSysteme" value="{{ prompt_systeme }}">

    <div class="chat-container">
        <div class="header">🎓 Code Tuteur IA — Terminale</div>
        <div class="author">Créé par Tsanta Niaina</div>
        
        <!-- Indicateur de téléchargement et de préparation de l'IA -->
        <div class="status-container">
            <span id="statusText">⏳ Initialisation et chargement du moteur d'IA local...</span>
            <div style="background: #333; border-radius: 3px; overflow: hidden;">
                <div class="progress-bar" id="progressBar"></div>
            </div>
        </div>

        <div class="chat-box" id="chatBox">
            <div class="msg bot">Salut ! Je suis ton IA de révision. Patiente pendant que je m'installe sur ton appareil, puis pose-moi tes questions !</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Pose ton exercice ou ta question..." onkeydown="if(event.key === 'Enter' && !document.getElementById('sendBtn').disabled) sendMessage()">
            <button id="sendBtn" onclick="sendMessage()" disabled>Envoyer</button>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE, prompt_systeme=PROMPT_SYSTEME)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
