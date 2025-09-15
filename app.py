"""
Dashboard CCI France Colombia - Agent MarIA
Application Streamlit principale
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement en premier
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Dashboard CCI France Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour élargir la sidebar
st.markdown("""
<style>
    /* Élargir la sidebar */
    .css-1d391kg, .css-1cypcdb, .css-1y4p8pa {
        width: 25rem !important;
        min-width: 25rem !important;
        max-width: 25rem !important;
    }
    
    /* Ajuster le contenu principal */
    .css-18e3th9, .css-1d391kg + .css-1d391kg {
        margin-left: 25rem !important;
    }
    
    /* Sidebar pour les nouvelles versions de Streamlit */
    section[data-testid="stSidebar"] {
        width: 25rem !important;
        min-width: 25rem !important;
    }
    
    section[data-testid="stSidebar"] .css-1lcbmhc {
        width: 25rem !important;
        min-width: 25rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Imports des modules
from utils.auth import check_authentication, show_logout_button
from components.kpis import show_kpis_section, show_period_selector
from components.conversations import show_conversations_section
from config.settings import APP_TITLE, APP_SUBTITLE, CCI_COLORS

def apply_custom_css():
    """
    Appliquer le CSS personnalisé pour le styling CCI
    """
    st.markdown(f"""
    <style>
    .main-header {{
        background: #2C3E50;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        border-left: 4px solid #3498DB;
    }}
    
    .main-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }}
    
    .main-header h3 {{
        color: #BDC3C7 !important;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
        font-size: 1rem;
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
        <h1>Dashboard CCI France Colombia</h1>
        <h3>Tableau de bord de l'agent MarIA</h3>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar_info():
    """
    Afficher les informations dans la sidebar
    """
    from datetime import datetime
    today = datetime.now().strftime("%d/%m/%Y")
    
    st.sidebar.markdown(f"""
    <div style="text-align: left; padding: 1rem 0.5rem;">
        <p style="color: #1B4F72; font-size: 1.1em; font-weight: 500;">Date : {today}</p>
    </div>
    """, unsafe_allow_html=True)


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
    
    # Navigation par boutons radio
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["KPIs", "Conversations"],
        index=0  # KPIs par défaut
    )
    
    # Sélecteur de période
    start_date, end_date = show_period_selector()
    
    # Bouton de déconnexion (plus bas)
    show_logout_button()
    
    # Validation des dates
    if start_date > end_date:
        st.error("❌ La date de début doit être antérieure à la date de fin.")
        return
    
    if page == "KPIs":
        show_kpis_section(start_date, end_date)
    else:
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
