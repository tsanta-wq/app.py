# app.py
import streamlit as st
import random
import requests
import datetime
import json

# --- CONFIGURATION EN LIGNE REQUISE ---
# REMPLACEZ CETTE URL par l'URL de votre serveur.
URL_API_SCORE = "https://webhook.site/7045f7e9-ab2b-403d-8f7b-949baea387c7" # Votre URL ici
# --------------------------------------

# --- 1. INITIALISATION DE L'ÉTAT (GÉRER LA PARTIE EN COURS) ---
# On utilise st.session_state pour mémoriser les variables entre les actions du joueur.
if 'partie_en_cours' not in st.session_state:
    st.session_state.partie_en_cours = False
    
if 'nombre_secret' not in st.session_state:
    st.session_state.nombre_secret = 0

if 'tentatives' not in st.session_state:
    st.session_state.tentatives = 0

if 'message_jeu' not in st.session_state:
    st.session_state.message_jeu = "Appuyez sur 'Démarrer une nouvelle partie' pour jouer."

# --- 2. LOGIQUE DU JEU ADAPTÉE À STREAMLIT ---

def demarrer_partie():
    """Réinitialise les variables pour un nouveau jeu."""
    st.session_state.partie_en_cours = True
    st.session_state.nombre_secret = random.randint(1, 100)
    st.session_state.tentatives = 0
    st.session_state.message_jeu = "J'ai choisi un nombre entre 1 et 100. À vous de deviner !"
    st.session_state.partie_terminee = False # Nouvelle variable pour gérer l'état final

def verifier_devinette(devine_str, nom_joueur):
    """Vérifie la devinette et met à jour l'état du jeu."""
    
    if not st.session_state.partie_en_cours or st.session_state.partie_terminee:
        st.session_state.message_jeu = "Veuillez démarrer une nouvelle partie."
        return

    try:
        devine = int(devine_str)
        st.session_state.tentatives += 1

        if devine < st.session_state.nombre_secret:
            st.session_state.message_jeu = f"Trop bas ! ⬇️ ({st.session_state.tentatives} tentatives)"
        elif devine > st.session_state.nombre_secret:
            st.session_state.message_jeu = f"Trop haut ! ⬆️ ({st.session_state.tentatives} tentatives)"
        else:
            # Succès et fin du jeu
            st.session_state.partie_terminee = True
            st.session_state.message_jeu = f"🥳 Bravo, {nom_joueur} ! Vous avez trouvé {st.session_state.nombre_secret} en **{st.session_state.tentatives} tentatives**."
            
            # Appel de la fonction d'envoi de score
            envoyer_score_en_ligne(nom_joueur, st.session_state.tentatives)

    except ValueError:
        st.session_state.message_jeu = "❌ Veuillez entrer un nombre entier valide."


def envoyer_score_en_ligne(nom, score):
    """Envoie le score de l'utilisateur à l'URL configurée (inchangé)."""
    
    donnees = {
        "joueur": nom,
        "score_tentatives": score,
        "date_heure": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jeu": "Devinette_Nombre_Web"
    }

    st.info("⏳ Envoi du score en ligne...")
    
    try:
        reponse = requests.post(
            URL_API_SCORE, 
            data=json.dumps(donnees), 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if reponse.status_code in [200, 201]:
            st.success(f"✅ Score envoyé avec succès à l'API ! (Code: {reponse.status_code})")
        else:
            st.warning(f"⚠️ Erreur lors de l'envoi du score. Le serveur a renvoyé un code: {reponse.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur de connexion ou réseau: Impossible d'envoyer le score en ligne. Détails: {e}")

# --- 3. MISE EN PAGE STREAMLIT (INTERFACE WEB) ---

st.set_page_config(page_title="Jeu de Devinette en Ligne", layout="centered")

st.title("🔢 Jeu de Devinette : De 1 à 100")
st.caption("Le score est envoyé en ligne après avoir trouvé le nombre.")

# Champ pour le nom du joueur (persistant)
nom_joueur = st.text_input("Quel est votre nom ou pseudo ?", key="pseudo_joueur")

# Bouton pour démarrer ou réinitialiser la partie
if st.button("Démarrer une nouvelle partie", type="primary"):
    if nom_joueur:
        demarrer_partie()
    else:
        st.warning("Veuillez entrer votre nom avant de commencer.")

st.markdown("---")

# Afficher l'état du jeu
st.info(st.session_state.message_jeu)

if st.session_state.partie_en_cours and not st.session_state.partie_terminee:
    
    # Formulaire de devinette
    with st.form(key='devinette_form'):
        devine_input = st.text_input(
            f"Tentative n°{st.session_state.tentatives + 1} : Entrez un nombre",
            key='current_devine'
        )
        
        # Le bouton de soumission appelle la fonction de vérification
        submit_button = st.form_submit_button(
            label='Soumettre la devinette',
            on_click=verifier_devinette,
            args=(devine_input, nom_joueur)
        )
