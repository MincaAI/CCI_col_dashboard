"""
Dashboard CCI France Colombia - Agent MarIA
Application Streamlit principale
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Dashboard CCI France Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des modules
from utils.auth import check_authentication, show_logout_button
from components.kpis import show_kpis_section, show_period_selector
from components.conversations import show_conversations_section
from database.connection import test_connection
from config.settings import APP_TITLE, APP_SUBTITLE, CCI_COLORS

def apply_custom_css():
    """
    Appliquer le CSS personnalisé pour le styling CCI
    """
    st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(90deg, {CCI_COLORS['primary']} 0%, {CCI_COLORS['secondary']} 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }}
    
    .main-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }}
    
    .main-header h3 {{
        color: #E8F4FD !important;
        margin: 0;
        font-weight: 300;
    }}
    
    .metric-container {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {CCI_COLORS['secondary']};
    }}
    
    .stMetric > label {{
        color: {CCI_COLORS['primary']} !important;
        font-weight: 600;
    }}
    
    .stSelectbox > label {{
        color: {CCI_COLORS['primary']} !important;
        font-weight: 600;
    }}
    
    .stDateInput > label {{
        color: {CCI_COLORS['primary']} !important;
        font-weight: 600;
    }}
    
    .sidebar-logo {{
        display: flex;
        justify-content: center;
        padding: 1rem 0;
    }}
    
    .conversation-agent {{
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid {CCI_COLORS['primary']};
    }}
    
    .conversation-client {{
        background-color: #FCE4EC;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid {CCI_COLORS['secondary']};
    }}
    
    /* Styling des boutons */
    .stButton > button {{
        background-color: {CCI_COLORS['primary']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        background-color: {CCI_COLORS['secondary']};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Styling des dataframes */
    .stDataFrame {{
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        overflow: hidden;
    }}
    
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """
    Afficher l'en-tête principal du dashboard
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>🇨🇴 {APP_TITLE}</h1>
        <h3>{APP_SUBTITLE}</h3>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar_info():
    """
    Afficher les informations dans la sidebar
    """
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <div style="text-align: center;">
            <h3 style="color: #1B4F72;">CCI France Colombia</h3>
            <p style="color: #666; font-size: 0.9em;">Dashboard Agent MarIA</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Informations sur l'agent MarIA
    st.sidebar.markdown("""
    ### 🤖 À propos de MarIA
    
    **MarIA** est l'assistante virtuelle de la CCI France Colombia qui aide les membres à:
    
    - 🎯 Identifier leurs besoins
    - 🤝 Trouver les services adaptés  
    - 📞 Connecter avec les bons contacts
    - 📋 Explorer nos 6 thèmes principaux
    
    ### 📊 Fonctionnalités du Dashboard
    
    - **KPIs**: Métriques clés de performance
    - **Conversations**: Analyse détaillée des échanges
    - **Résumés IA**: Synthèses automatiques
    - **Export**: Données exportables
    """)

def show_connection_status():
    """
    Afficher le statut de connexion à la base de données
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔗 Statut de connexion")
        
        if test_connection():
            st.success("✅ Base de données connectée")
        else:
            st.error("❌ Erreur de connexion")
            st.stop()

def main():
    """
    Fonction principale de l'application
    """
    # Appliquer le CSS personnalisé
    apply_custom_css()
    
    # Vérifier l'authentification
    if not check_authentication():
        return
    
    # Afficher l'en-tête
    show_header()
    
    # Sidebar avec informations
    show_sidebar_info()
    show_connection_status()
    
    # Sélecteur de période
    start_date, end_date = show_period_selector()
    
    # Bouton de déconnexion
    show_logout_button()
    
    # Validation des dates
    if start_date > end_date:
        st.error("❌ La date de début doit être antérieure à la date de fin.")
        return
    
    # Affichage de la période sélectionnée
    st.info(f"📅 Période d'analyse: du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
    
    # Sections principales du dashboard
    tab1, tab2 = st.tabs(["📊 KPIs", "💬 Conversations"])
    
    with tab1:
        show_kpis_section(start_date, end_date)
    
    with tab2:
        show_conversations_section(start_date, end_date)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Dashboard CCI France Colombia - Agent MarIA | 
        Développé avec ❤️ par <strong>MincaAI</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
