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

# Session persistante avec cache
@st.cache_data(ttl=24*3600)  # Cache pendant 24 heures
def get_persistent_session():
    """Créer une session persistante qui survit aux refreshs"""
    return {
        'authenticated': False,
        'login_time': None,
        'session_id': None
    }

def get_session():
    """Récupérer ou créer la session persistante"""
    if 'persistent_auth' not in st.session_state:
        st.session_state.persistent_auth = get_persistent_session()
    return st.session_state.persistent_auth

def check_authentication():
    """
    Vérifier l'authentification avec session persistante (24h)
    """
    session = get_session()
    
    # Vérifier si la session a expiré (24 heures)
    if session['authenticated'] and session['login_time']:
        current_time = time.time()
        session_duration = current_time - session['login_time']
        
        # Session expire après 24 heures (86400 secondes)
        if session_duration > 86400:
            session['authenticated'] = False
            session['login_time'] = None
            session['session_id'] = None
            # Vider le cache pour forcer une nouvelle authentification
            get_persistent_session.clear()
            st.warning("⏰ Session expirée après 24h. Veuillez vous reconnecter.")
    
    if not session['authenticated']:
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
                    session = get_session()
                    session['authenticated'] = True
                    session['login_time'] = time.time()
                    session['session_id'] = hashlib.md5(f"{username}_{time.time()}".encode()).hexdigest()
                    
                    # Mettre à jour aussi st.session_state pour compatibilité
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = session['login_time']
                    
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
    session = get_session()
    session['authenticated'] = False
    session['login_time'] = None
    session['session_id'] = None
    
    # Nettoyer aussi st.session_state
    st.session_state.authenticated = False
    st.session_state.login_time = None
    if 'username' in st.session_state:
        del st.session_state.username
    
    # Vider le cache
    get_persistent_session.clear()
    st.rerun()

def show_logout_button():
    """
    Afficher le bouton de déconnexion dans la sidebar
    """
    with st.sidebar:
        st.markdown("---")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            logout()
