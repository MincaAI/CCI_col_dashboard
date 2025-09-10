"""
Composants KPIs pour le dashboard
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from database.queries import get_kpi_data, get_completion_candidates
from utils.llm_analysis import analyze_conversation_completion
from config.settings import CCI_COLORS

def show_kpis_section(start_date, end_date):
    """
    Afficher la section KPIs du dashboard
    """
    st.header("📊 Indicateurs Clés de Performance")
    
    # Récupérer les données KPI
    with st.spinner("Chargement des KPIs..."):
        kpi_data = get_kpi_data(start_date, end_date)
        completion_data = get_completion_candidates(start_date, end_date)
    
    # Calculer le taux de completion
    completion_rate = calculate_completion_rate(completion_data)
    
    # Afficher les métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Nombre total d'utilisateurs",
            value=int(kpi_data['total_users']),
            help="Nombre unique de conversations WhatsApp"
        )
    
    with col2:
        st.metric(
            label="💬 Longueur moyenne des conversations",
            value=f"{kpi_data['avg_conversation_length']} messages",
            help="Nombre moyen de messages par conversation"
        )
    
    with col3:
        st.metric(
            label="✅ Taux de completion",
            value=f"{completion_rate:.1f}%",
            help="Pourcentage de conversations terminées avec un contact fourni"
        )
    
    with col4:
        total_messages = kpi_data['daily_messages']['message_count'].sum() if not kpi_data['daily_messages'].empty else 0
        st.metric(
            label="📨 Total des messages",
            value=int(total_messages),
            help="Nombre total de messages sur la période"
        )
    
    # Graphiques
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_daily_messages_chart(kpi_data['daily_messages'])
    
    with col2:
        show_completion_rate_chart(completion_data)

def calculate_completion_rate(completion_data):
    """
    Calculer le taux de completion en analysant les derniers messages
    """
    if completion_data.empty:
        return 0.0
    
    completed_count = 0
    total_count = len(completion_data)
    
    # Analyser chaque dernier message pour détecter la completion
    for _, row in completion_data.iterrows():
        if analyze_conversation_completion(row['content']):
            completed_count += 1
    
    return (completed_count / total_count) * 100 if total_count > 0 else 0.0

def show_daily_messages_chart(daily_messages_df):
    """
    Afficher le graphique des messages par jour
    """
    st.subheader("📈 Messages par jour")
    
    if daily_messages_df.empty:
        st.info("Aucune donnée disponible pour cette période")
        return
    
    fig = px.line(
        daily_messages_df, 
        x='date', 
        y='message_count',
        title="Évolution des messages par jour",
        labels={'message_count': 'Nombre de messages', 'date': 'Date'}
    )
    
    fig.update_traces(
        line_color=CCI_COLORS['primary'],
        line_width=3
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_completion_rate_chart(completion_data):
    """
    Afficher un graphique du taux de completion
    """
    st.subheader("✅ Analyse de completion")
    
    if completion_data.empty:
        st.info("Aucune donnée disponible pour cette période")
        return
    
    # Analyser les conversations pour la completion
    completed = 0
    incomplete = 0
    
    for _, row in completion_data.iterrows():
        if analyze_conversation_completion(row['content']):
            completed += 1
        else:
            incomplete += 1
    
    # Créer un graphique en secteurs
    labels = ['Complètes', 'Incomplètes']
    values = [completed, incomplete]
    colors = [CCI_COLORS['secondary'], '#CCCCCC']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=0.4,
        marker_colors=colors
    )])
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        title="Répartition des conversations",
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_period_selector():
    """
    Afficher le sélecteur de période
    """
    st.sidebar.header("📅 Période d'analyse")
    
    # Options prédéfinies
    period_options = {
        "7 derniers jours": timedelta(days=7),
        "30 derniers jours": timedelta(days=30),
        "3 derniers mois": timedelta(days=90),
        "Personnalisé": None
    }
    
    selected_period = st.sidebar.selectbox(
        "Choisir une période",
        options=list(period_options.keys()),
        index=1  # 30 derniers jours par défaut
    )
    
    if selected_period == "Personnalisé":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Date de début", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Date de fin", value=datetime.now())
    else:
        end_date = datetime.now().date()
        start_date = (datetime.now() - period_options[selected_period]).date()
    
    return start_date, end_date
