"""
Module d'authentification pour le dashboard
"""
import streamlit as st
from config.settings import AUTH_USERNAME, AUTH_PASSWORD

def check_authentication():
    """
    Vérifier l'authentification de l'utilisateur
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
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
                    st.session_state.authenticated = True
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

def authenticate_user(username, password):
    """
    Authentifier l'utilisateur avec les credentials
    """
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def logout():
    """
    Déconnecter l'utilisateur
    """
    st.session_state.authenticated = False
    st.rerun()

def show_logout_button():
    """
    Afficher le bouton de déconnexion dans la sidebar
    """
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            logout()
