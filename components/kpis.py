"""
Composants KPIs pour le dashboard
"""
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from database.queries import get_kpi_data, get_completion_stats, get_engaged_conversations_count
from config.settings import CCI_COLORS

def show_loading_placeholders():
    """
    Afficher des placeholders pendant le chargement des KPIs
    """
    # Placeholders pour les métriques - 5 colonnes maintenant
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, transparent 25%, transparent 50%, #f0f0f0 50%, #f0f0f0 75%, transparent 75%);
            background-size: 20px 20px;
            height: 100px;
            border-radius: 10px;
            animation: loading 1.5s infinite linear;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        ">
            <div>🔄 Chargement...</div>
        </div>
        <style>
        @keyframes loading {
            0% { background-position: 0 0; }
            100% { background-position: 20px 0; }
        }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, transparent 25%, transparent 50%, #f0f0f0 50%, #f0f0f0 75%, transparent 75%);
            background-size: 20px 20px;
            height: 100px;
            border-radius: 10px;
            animation: loading 1.5s infinite linear;
            animation-delay: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        ">
            <div>📊 Calcul...</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, transparent 25%, transparent 50%, #f0f0f0 50%, #f0f0f0 75%, transparent 75%);
            background-size: 20px 20px;
            height: 100px;
            border-radius: 10px;
            animation: loading 1.5s infinite linear;
            animation-delay: 0.6s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        ">
            <div>✅ Analyse...</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, transparent 25%, transparent 50%, #f0f0f0 50%, #f0f0f0 75%, transparent 75%);
            background-size: 20px 20px;
            height: 100px;
            border-radius: 10px;
            animation: loading 1.5s infinite linear;
            animation-delay: 0.9s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        ">
            <div>📈 Préparation...</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, transparent 25%, transparent 50%, #f0f0f0 50%, #f0f0f0 75%, transparent 75%);
            background-size: 20px 20px;
            height: 100px;
            border-radius: 10px;
            animation: loading 1.5s infinite linear;
            animation-delay: 1.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        ">
            <div>💬 Analyse...</div>
        </div>
        """, unsafe_allow_html=True)

def show_kpis_section(start_date, end_date):
    """
    Afficher la section KPIs du dashboard avec indicateurs de chargement
    """
    st.header("Indicateurs Clés de Performance")
    
    # Conteneur principal pour les placeholders
    main_container = st.container()
    
    with main_container:
        # Afficher des placeholders pendant le chargement
        placeholders_container = st.empty()
        
        with placeholders_container.container():
            # Afficher les placeholders de chargement
            show_loading_placeholders()
            
            # Barre de progression et statut
            progress_col1, progress_col2 = st.columns([3, 1])
            with progress_col1:
                progress_bar = st.progress(0)
                status_text = st.empty()
            with progress_col2:
                st.markdown("⏳ **Chargement en cours...**")
        
        # Récupérer les données KPI avec feedback détaillé
        try:
            # Étape 1: Chargement des données KPI
            status_text.text("🔄 Récupération des données KPI...")
            progress_bar.progress(20)
            kpi_data = get_kpi_data(start_date, end_date)
            
            # Étape 2: Chargement des statistiques de completion
            status_text.text("📊 Analyse des taux de completion...")
            progress_bar.progress(50)
            completion_stats_df = get_completion_stats(start_date, end_date)
            
            # Étape 3: Chargement des conversations engagées
            status_text.text("💬 Calcul des conversations engagées...")
            progress_bar.progress(75)
            engaged_df = get_engaged_conversations_count(start_date, end_date)
            
            # Finalisation
            status_text.text("✨ Finalisation de l'affichage...")
            progress_bar.progress(100)
            
            # Extraire les valeurs
            completion_stats = {
                'total': completion_stats_df.iloc[0]['total_conversations'] if not completion_stats_df.empty else 0,
                'completed': completion_stats_df.iloc[0]['completed_count'] if not completion_stats_df.empty else 0,
                'incomplete': completion_stats_df.iloc[0]['incomplete_count'] if not completion_stats_df.empty else 0,
                'not_analyzed': completion_stats_df.iloc[0]['not_analyzed_count'] if not completion_stats_df.empty else 0
            }
            
            engaged_count = engaged_df.iloc[0]['engaged_conversations'] if not engaged_df.empty else 0
            
            # Nettoyer complètement les placeholders
            placeholders_container.empty()
            
        except Exception as e:
            placeholders_container.empty()
            # Afficher des valeurs par défaut au lieu d'une erreur
            st.info("📊 Données en cours de chargement... Veuillez patienter.")
            return
    
    # Afficher les métriques principales avec protection contre les erreurs - 5 colonnes maintenant
    col1, col2, col3, col4, col5 = st.columns(5)
    
    try:
        with col1:
            total_users = kpi_data.get('total_users', 0) if kpi_data else 0
            st.metric(
                label="👥 Total conversations",
                value=int(total_users) if total_users else 0,
                help="Nombre unique de conversations WhatsApp"
            )
        
        with col2:
            st.metric(
                label="💬 Conversations engagées",
                value=int(engaged_count) if engaged_count else 0,
                help="Conversations avec plus de 2 messages"
            )
        
        with col3:
            avg_length = kpi_data.get('avg_conversation_length', 0) if kpi_data else 0
            st.metric(
                label="📏 Longueur moyenne",
                value=f"{avg_length}",
                help="Nombre moyen de messages par conversation"
            )
        
        with col4:
            completed_count = completion_stats['completed']
            st.metric(
                label="✅ Conversations complètes",
                value=int(completed_count) if completed_count else 0,
                help="Conversations terminées avec un contact fourni"
            )
        
        with col5:
            incomplete_count = completion_stats['incomplete']
            st.metric(
                label="⏳ Conversations incomplètes",
                value=int(incomplete_count) if incomplete_count else 0,
                help="Conversations non terminées ou sans contact fourni"
            )
    except Exception:
        # En cas d'erreur, afficher des valeurs par défaut
        with col1:
            st.metric("👥 Total conversations", "0")
        with col2:
            st.metric("💬 Conversations engagées", "0")
        with col3:
            st.metric("📏 Longueur moyenne", "0")
        with col4:
            st.metric("✅ Conversations complètes", "0")
        with col5:
            st.metric("⏳ Conversations incomplètes", "0")
    
    # Graphiques avec indicateurs de chargement
    st.markdown("---")
    
    # Conteneurs pour les graphiques
    charts_container = st.empty()
    
    with charts_container.container():
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("Génération du graphique des conversations..."):
                show_daily_conversations_chart(kpi_data['daily_conversations'])
        
        with col2:
            with st.spinner("Génération du graphique de completion..."):
                show_completion_rate_chart(completion_stats)


def show_daily_conversations_chart(daily_conversations_df):
    """
    Afficher le graphique en barres des nouvelles conversations par jour
    """
    st.subheader("Nouvelles conversations par jour")
    
    if daily_conversations_df.empty:
        st.info("Aucune donnée disponible pour cette période")
        return
    
    fig = px.bar(
        daily_conversations_df, 
        x='date', 
        y='new_conversations',
        title="Nouvelles conversations démarrées chaque jour",
        text='new_conversations'  # Afficher les valeurs sur les barres
    )
    
    fig.update_traces(
        marker_color=CCI_COLORS['primary'],
        hovertemplate='<b>%{x}</b><br>Nouvelles conversations: %{y}<extra></extra>',
        textposition='outside',  # Placer le texte au-dessus des barres
        textfont_size=12
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="",  # Supprimer le titre de l'axe X
        yaxis_title="",  # Supprimer le titre de l'axe Y
        yaxis=dict(
            dtick=1,  # Forcer les intervalles de 1 pour éviter les 0,5
            tickmode='linear'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_completion_rate_chart(completion_stats):
    """
    Afficher un graphique du taux de completion depuis les données de la base
    """
    st.subheader("Analyse de completion")
    
    if not completion_stats or completion_stats['total'] == 0:
        st.info("Aucune donnée disponible pour cette période")
        return
    
    completed = completion_stats['completed']
    incomplete = completion_stats['incomplete']
    not_analyzed = completion_stats['not_analyzed']
    
    # Créer un graphique en secteurs
    labels = []
    values = []
    colors = []
    
    if completed > 0:
        labels.append('Complètes')
        values.append(completed)
        colors.append(CCI_COLORS['secondary'])
    
    if incomplete > 0:
        labels.append('Incomplètes')
        values.append(incomplete)
        colors.append('#CCCCCC')
    
    if not_analyzed > 0:
        labels.append('Non analysées')
        values.append(not_analyzed)
        colors.append('#FFA500')
    
    if not values:
        st.info("Aucune donnée de completion disponible")
        return
    
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
    Afficher le sélecteur de période simple
    """
    st.sidebar.header("📅 Période")
    
    # Sélecteur de dates simple
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Du", 
            value=datetime(2025, 8, 1).date()
        )
    with col2:
        end_date = st.date_input(
            "Au", 
            value=datetime.now().date()
        )
    
    return start_date, end_date
