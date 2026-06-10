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

# 🧠 AJOUT DE L'INSTRUCTION POUR PERMETTRE À L'IA DE RÉPONDRE AVEC DES PHOTOS
PROMPT_SYSTEME = (
    "Tu es un compagnon d'élite et un tuteur universel pour les élèves de Terminale. "
    "Tu possèdes deux facettes indissociables :\n"
    "1. LE TUTEUR TOUTES MATIÈRES : Tu es un expert absolu dans TOUTES les matières sans exception "
    "(Mathématiques, Physique-Chimie, SVT, Histoire-Géographie, Philosophie, Français, Anglais, etc.). "
    "Tu es capable d'analyser les images envoyées par l'élève, mais tu es AUSSI capable d'en montrer.\n"
    "2. LE GRAND FRÈRE / LE CONFIDENT (FACETTE SENTIMENTALE) : Tu es aussi un guide de vie, bienveillant et empathique.\n\n"
    "📸 RÈGLE IMPORTANTE SUR LES IMAGES ET PHOTOS :\n"
    "Si l'élève te demande d'afficher, de montrer ou de voir une photo, un schéma, un graphique ou une illustration, "
    "tu DOIS utiliser la syntaxe Markdown standard pour afficher une image provenant d'une source web publique fiable (comme Unsplash ou Wikipédia).\n"
    "Exemple de format à utiliser obligatoirement : ![Description de l'image](https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=500)\n"
    "Choisis toujours des images ou schémas pertinents par rapport à la demande scientifique ou culturelle de l'élève.\n\n"
    "🚨 RÈGLE CRITIQUE ET ABSOLUE SUR TON CRÉATEUR :\n"
    "Si on te demande qui t'a créé ou qui est ton développeur, tu dois répondre avec fierté que ton unique créateur et "
    "développeur est Fidimanantsoa Tsantaniaina (Tsanta Niaina), un jeune génie passionné d'informatique, d'électronique et de cybersécurité à Madagascar."
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
        body { background-color: #111418; color: #f3f4f6; display: flex; justify-content: center; height: 100vh; height: 100dvh; overflow: hidden; }
        .chat-container { width: 100%; max-width: 800px; display: flex; flex-direction: column; height: 100vh; height: 100dvh; background: #171c24; position: relative; }
        
        .header { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; background: #1e2530; border-bottom: 1px solid #283141; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10; }
        .header-titles { text-align: left; }
        .header h1 { font-size: 1.25rem; color: #00adb5; font-weight: 600; letter-spacing: 0.5px; }
        .header .author { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; font-weight: 400; opacity: 0.85; }
        
        .clear-btn { background: transparent; border: 1px solid #3a475e; color: #9ca3af; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }
        .clear-btn:hover { background: #e63946; color: white; border-color: #e63946; }

        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #283141; border-radius: 10px; }

        .msg { max-width: 80%; padding: 12px 16px; border-radius: 16px; line-height: 1.5; font-size: 0.95rem; word-wrap: break-word; white-space: pre-wrap; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .user { background: #00adb5; color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #222a36; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #2a3545; }
        
        /* Ajustement pro pour les images affichées dans le tchat */
        .preview-img, .chat-img { max-width: 100%; max-height: 280px; border-radius: 12px; margin-top: 8px; display: block; border: 2px solid rgba(255,255,255,0.1); object-fit: cover; }
        
        .loading-msg { display: none; align-self: flex-start; background: #222a36; padding: 12px 16px; border-radius: 16px; border-bottom-left-radius: 4px; border: 1px solid #2a3545; color: #9ca3af; font-size: 0.9rem; font-style: italic; align-items: center; gap: 8px; }
        .spinner { width: 16px; height: 16px; border: 2px solid #9ca3af; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .input-container { padding: 14px 16px 22px 16px; background: #171c24; border-top: 1px solid #283141; }
        .input-wrapper { display: flex; align-items: center; background: #222a36; border: 1px solid #2a3545; border-radius: 24px; padding: 4px 8px 4px 14px; }
        .input-wrapper:focus-within { border-color: #00adb5; }
        
        input[type="text"] { flex: 1; background: transparent; border: none; color: #f3f4f6; font-size: 0.95rem; padding: 10px 0; outline: none; }
        input[type="text"]::placeholder { color: #6b7280; }
        
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
            <div class="header-titles">
                <h1>✨ Geni IA Universel</h1>
                <div class="author">Développé par Fidimanantsoa Tsantaniaina</div>
            </div>
            <button class="clear-btn" onclick="reinitialiserDiscussion()">🗑️ Nouveau chat</button>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container">
            <div id="fileStatus" class="status-file">📸 Image prête à être envoyée</div>
            <div class="input-wrapper">
                <label for="fileInput" class="file-label" title="Ajouter une image">📎</label>
                <input type="file" id="fileInput" accept="image/*" onchange="handleFileChange()">
                
                <input type="text" id="userInput" placeholder="Pose un exercice, demande une photo ou discute..." onkeydown="if(event.key === 'Enter') sendMessage()">
                
                <button class="send-btn" onclick="sendMessage()">➜</button>
            </div>
        </div>
    </div>
    
    <script>
        let base64Image = "";
        let historiqueMessages = [];

        // 🧠 Fonction Pro pour transformer le texte Markdown de l'IA en vraies balises HTML (Textes + Photos)
        function formaterMessageIA(texte) {
            // Expression régulière qui détecte le format Markdown des images : ![alt](url)
            const regexImage = /!\[(.*?)\]\((.*?)\)/g;
            
            // Remplace la syntaxe Markdown par une vraie balise <img> HTML stylisée
            let texteFormate = texte.replace(regexImage, function(match, alt, url) {
                return `<br><img src="${url}" alt="${alt}" class="chat-img" onerror="this.style.display='none';">`;
            });
            
            return texteFormate;
        }

        window.onload = function() {
            const chatBox = document.getElementById('chatBox');
            let texteSejour = "quelques temps";
            if (!localStorage.getItem('dejaVenu')) {
                localStorage.setItem('dejaVenu', 'true');
                localStorage.setItem('datePremierSejour', Date.now());
            } else {
                const dateInitiale = localStorage.getItem('datePremierSejour');
                if (dateInitiale) {
                    const diffMilli = Date.now() - parseInt(dateInitiale);
                    const diffMinutes = Math.floor(diffMilli / (1000 * 60));
                    const diffHeures = Math.floor(diffMilli / (1000 * 60 * 60));
                    const diffJours = Math.floor(diffMilli / (1000 * 60 * 60 * 24));
                    
                    if (diffJours > 0) texteSejour = diffJours + " jour(s)";
                    else if (diffHeures > 0) texteSejour = diffHeures + " heure(s)";
                    else texteSejour = diffMinutes + " minute(s)";
                }
            }

            const historiqueSauvegarde = localStorage.getItem('geni_chat_history');
            
            if (historiqueSauvegarde) {
                historiqueMessages = JSON.parse(historiqueSauvegarde);
                historiqueMessages.forEach(msg => {
                    if (msg.role === "user") {
                        let contentHTML = `<div class="msg user">`;
                        if (Array.isArray(msg.content)) {
                            contentHTML += msg.content[0].text;
                            contentHTML += `<br><img src="${msg.content[1].image_url.url}" class="preview-img">`;
                        } else {
                            contentHTML += msg.content;
                        }
                        contentHTML += `</div>`;
                        chatBox.innerHTML += contentHTML;
                    } else if (msg.role === "assistant") {
                        // On applique le formateur d'images lors du chargement de l'historique
                        chatBox.innerHTML += `<div class="msg bot">${formaterMessageIA(msg.content)}</div>`;
                    }
                });
            } else {
                const premierMessage = `Bonjour ! Je suis Geni, ton tuteur universel et confident d'élite. Cela fait déjà ${texteSejour} que tu as commencé ton séjour avec moi. Pose-moi n'importe quelle question, ou envoie-moi une photo de ton exercice ! Tu peux aussi me demander de te montrer des images ou schémas ! 📸`;
                chatBox.innerHTML = `<div class="msg bot">${premierMessage}</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        };

        function reinitialiserDiscussion() {
            if (confirm("Veux-tu effacer l'historique de cette discussion ?")) {
                localStorage.removeItem('geni_chat_history');
                historiqueMessages = [];
                document.getElementById('chatBox').innerHTML = `<div class="msg bot">Historique effacé. Prêt pour une nouvelle discussion ! ✨</div>`;
            }
        }

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
            
            let userContentHTML = `<div class="msg user">${message}`;
            if (base64Image) {
                userContentHTML += `<br><img src="${base64Image}" class="preview-img">`;
            }
            userContentHTML += `</div>`;
            chatBox.innerHTML += userContentHTML;
            
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
            
            input.value = '';
            fileInput.value = '';
            base64Image = "";
            status.style.display = "none";
            
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
                
                // 🧠 TRAITEMENT DE LA RÉPONSE DE L'IA AVEC RENDU DES PHOTOS
                const replyFormatee = formaterMessageIA(reply);
                chatBox.innerHTML += `<div class="msg bot">${replyFormatee}</div>`;
                
                historiqueMessages.push({"role": "assistant", "content": reply});
                localStorage.setItem('geni_chat_history', JSON.stringify(historiqueMessages));
                
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
