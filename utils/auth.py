"""
Module d'authentification pour le dashboard avec session persistante
"""
import os
import time
import hashlib
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from config.settings import AUTH_USERNAME, AUTH_PASSWORD

def get_session():
    """Récupérer ou créer la session"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = None
        st.session_state.session_id = None
    
    return {
        'authenticated': st.session_state.authenticated,
        'login_time': st.session_state.login_time,
        'session_id': st.session_state.session_id
    }

def check_authentication():
    """
    Vérifier l'authentification avec session persistante (24h)
    """
    # Initialiser la session si nécessaire
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = None
        st.session_state.session_id = None
    
    # Vérifier si la session a expiré (24 heures)
    if st.session_state.authenticated and st.session_state.login_time:
        current_time = time.time()
        session_duration = current_time - st.session_state.login_time
        
        # Session expire après 24 heures (86400 secondes)
        if session_duration > 86400:
            st.session_state.authenticated = False
            st.session_state.login_time = None
            st.session_state.session_id = None
            st.warning("⏰ Session expirée après 24h. Veuillez vous reconnecter.")
    
    if not st.session_state.authenticated:
        show_login_form()
        return False
    
    return True

def show_login_form():
    """
    Afficher le formulaire de connexion
    """
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 50vh;">
        <div style="text-align: center; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #1B4F72; margin-bottom: 2rem;">🔐 Connexion Dashboard CCI</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur", placeholder="cci-col")
            password = st.text_input("Mot de passe", type="password", placeholder="Mot de passe")
            submit_button = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit_button:
                if authenticate_user(username, password):
                    # Authentification réussie
                    st.session_state.authenticated = True
                    st.session_state.login_time = time.time()
                    st.session_state.session_id = hashlib.md5(f"{username}_{time.time()}".encode()).hexdigest()
                    st.session_state.username = username
                    
                    st.success("✅ Connexion réussie ! Session persistante 24h.")
                    st.rerun()
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

def authenticate_user(username, password):
    """
    Authentifier l'utilisateur avec les credentials
    """
    if not AUTH_USERNAME or not AUTH_PASSWORD:
        st.error("❌ Configuration d'authentification manquante. Vérifiez le fichier .env")
        return False
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def logout():
    """
    Déconnecter l'utilisateur
    """
    # Nettoyer la session
    st.session_state.authenticated = False
    st.session_state.login_time = None
    st.session_state.session_id = None
    if 'username' in st.session_state:
        del st.session_state.username
    
    st.rerun()

def show_logout_button():
    """
    Afficher le bouton de déconnexion dans la sidebar
    """
    with st.sidebar:
        st.markdown("---")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            logout()
