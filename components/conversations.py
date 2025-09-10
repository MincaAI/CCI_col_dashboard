"""
Composants de la section conversations
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database.queries import get_conversations_summary_data, get_conversation_messages
from utils.llm_analysis import generate_conversation_summary, extract_themes_analysis, analyze_conversation_completion
from config.settings import MARIA_THEMES
import io

def show_conversations_section(start_date, end_date):
    """
    Afficher la section conversations du dashboard
    """
    st.header("💬 Conversations et Analyses")
    
    # Récupérer les données des conversations
    with st.spinner("Chargement des conversations..."):
        conversations_df = get_conversations_summary_data(start_date, end_date)
    
    if conversations_df.empty:
        st.info("Aucune conversation trouvée pour cette période.")
        return
    
    # Options d'affichage
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"📋 {len(conversations_df)} conversations trouvées")
    
    with col2:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Générer analyses LLM", use_container_width=True):
            generate_all_summaries(conversations_df)
    
    # Tableau des conversations avec pagination
    show_conversations_table(conversations_df)
    
    # Section d'analyse détaillée
    st.markdown("---")
    show_detailed_analysis_section(conversations_df)

def show_conversations_table(conversations_df):
    """
    Afficher le tableau des conversations avec pagination
    """
    st.subheader("📋 Tableau des conversations")
    
    # Configuration de la pagination
    items_per_page = 20
    total_conversations = len(conversations_df)
    total_pages = (total_conversations - 1) // items_per_page + 1
    
    # Sélecteur de page
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox(
                "Page",
                range(1, total_pages + 1),
                format_func=lambda x: f"Page {x} / {total_pages}"
            )
        
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_conversations)
        page_df = conversations_df.iloc[start_idx:end_idx]
    else:
        page_df = conversations_df
    
    # Préparer les données pour l'affichage
    display_df = prepare_display_dataframe(page_df)
    
    # Configuration des colonnes
    column_config = {
        "Chat ID": st.column_config.TextColumn("ID Conversation", width="small"),
        "Début": st.column_config.DatetimeColumn("Début", format="DD/MM/YYYY HH:mm"),
        "Fin": st.column_config.DatetimeColumn("Fin", format="DD/MM/YYYY HH:mm"),
        "Messages": st.column_config.NumberColumn("Total Messages"),
        "Client": st.column_config.NumberColumn("Messages Client"),
        "Agent": st.column_config.NumberColumn("Messages Agent"),
        "Durée": st.column_config.TextColumn("Durée"),
        "Analyser": st.column_config.LinkColumn("Analyser")
    }
    
    # Afficher le tableau
    event = st.dataframe(
        display_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Actions sur la sélection
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_chatid = page_df.iloc[selected_idx]['chatid']
        show_conversation_details(selected_chatid)

def prepare_display_dataframe(conversations_df):
    """
    Préparer le DataFrame pour l'affichage dans le tableau
    """
    display_df = conversations_df.copy()
    
    # Calculer la durée
    display_df['duration'] = display_df['end_time'] - display_df['start_time']
    display_df['duration_str'] = display_df['duration'].apply(format_duration)
    
    # Renommer et sélectionner les colonnes
    display_df = display_df.rename(columns={
        'chatid': 'Chat ID',
        'start_time': 'Début',
        'end_time': 'Fin',
        'message_count': 'Messages',
        'customer_messages': 'Client',
        'agent_messages': 'Agent',
        'duration_str': 'Durée'
    })
    
    return display_df[['Chat ID', 'Début', 'Fin', 'Messages', 'Client', 'Agent', 'Durée']]

def format_duration(duration):
    """
    Formater la durée en format lisible
    """
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def show_conversation_details(chatid):
    """
    Afficher les détails d'une conversation sélectionnée
    """
    st.markdown("---")
    st.subheader(f"🔍 Détails de la conversation: {chatid}")
    
    # Récupérer les messages de la conversation
    with st.spinner("Chargement des messages..."):
        messages_df = get_conversation_messages(chatid)
    
    if messages_df.empty:
        st.error("Impossible de récupérer les messages de cette conversation.")
        return
    
    # Onglets pour différentes vues
    tab1, tab2, tab3 = st.tabs(["💬 Messages", "📋 Résumé LLM", "🎯 Analyse des thèmes"])
    
    with tab1:
        show_conversation_messages(messages_df)
    
    with tab2:
        show_conversation_summary(messages_df, chatid)
    
    with tab3:
        show_themes_analysis(messages_df, chatid)

def show_conversation_messages(messages_df):
    """
    Afficher les messages de la conversation
    """
    st.markdown("### Messages de la conversation")
    
    for _, message in messages_df.iterrows():
        if message['role'] == 'agent':
            # Message de l'agent (MarIA)
            st.markdown(f"""
            <div style="background-color: #E3F2FD; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #1B4F72;">
                <strong>🤖 MarIA</strong> <span style="color: #666; font-size: 0.8em;">{message['created_at']}</span><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Message du client
            st.markdown(f"""
            <div style="background-color: #FCE4EC; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #E91E63;">
                <strong>👤 Client</strong> <span style="color: #666; font-size: 0.8em;">{message['created_at']}</span><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)

def show_conversation_summary(messages_df, chatid):
    """
    Afficher le résumé LLM de la conversation
    """
    st.markdown("### Résumé généré par IA")
    
    # Vérifier si le résumé existe déjà en session
    summary_key = f"summary_{chatid}"
    
    if summary_key not in st.session_state:
        if st.button("🎯 Générer le résumé", key=f"generate_summary_{chatid}"):
            with st.spinner("Génération du résumé en cours..."):
                summary = generate_conversation_summary(messages_df)
                st.session_state[summary_key] = summary
    
    if summary_key in st.session_state:
        st.markdown(st.session_state[summary_key])
        
        # Bouton pour régénérer
        if st.button("🔄 Régénérer", key=f"regenerate_summary_{chatid}"):
            with st.spinner("Régénération du résumé..."):
                summary = generate_conversation_summary(messages_df)
                st.session_state[summary_key] = summary
                st.rerun()

def show_themes_analysis(messages_df, chatid):
    """
    Afficher l'analyse des thèmes MarIA
    """
    st.markdown("### Analyse des 6 thèmes de MarIA")
    
    # Vérifier si l'analyse existe déjà en session
    themes_key = f"themes_{chatid}"
    
    if themes_key not in st.session_state:
        if st.button("🎯 Analyser les thèmes", key=f"analyze_themes_{chatid}"):
            with st.spinner("Analyse des thèmes en cours..."):
                analysis = extract_themes_analysis(messages_df)
                st.session_state[themes_key] = analysis
    
    if themes_key in st.session_state:
        st.markdown("**Thèmes abordés dans la conversation:**")
        st.text(st.session_state[themes_key])
        
        # Bouton pour régénérer
        if st.button("🔄 Réanalyser", key=f"reanalyze_themes_{chatid}"):
            with st.spinner("Réanalyse des thèmes..."):
                analysis = extract_themes_analysis(messages_df)
                st.session_state[themes_key] = analysis
                st.rerun()

def show_detailed_analysis_section(conversations_df):
    """
    Afficher la section d'analyse détaillée
    """
    st.subheader("📊 Analyses détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exporter les conversations", use_container_width=True):
            export_conversations_data(conversations_df)
    
    with col2:
        if st.button("🎯 Analyse complète LLM", use_container_width=True):
            run_bulk_analysis(conversations_df)

def generate_all_summaries(conversations_df):
    """
    Générer les résumés pour toutes les conversations
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_conversations = len(conversations_df)
    
    for i, (_, conv) in enumerate(conversations_df.iterrows()):
        status_text.text(f"Analyse de la conversation {i+1}/{total_conversations}...")
        
        # Récupérer les messages et générer le résumé
        messages_df = get_conversation_messages(conv['chatid'])
        if not messages_df.empty:
            summary = generate_conversation_summary(messages_df)
            st.session_state[f"summary_{conv['chatid']}"] = summary
        
        progress_bar.progress((i + 1) / total_conversations)
    
    status_text.text("✅ Toutes les analyses sont terminées !")
    st.success("Résumés générés avec succès !")

def export_conversations_data(conversations_df):
    """
    Exporter les données des conversations
    """
    # Créer un DataFrame d'export avec plus de détails
    export_data = []
    
    for _, conv in conversations_df.iterrows():
        messages_df = get_conversation_messages(conv['chatid'])
        
        if not messages_df.empty:
            # Récupérer le résumé s'il existe
            summary_key = f"summary_{conv['chatid']}"
            summary = st.session_state.get(summary_key, "Non généré")
            
            # Analyser la completion
            last_message = messages_df.iloc[-1]['content']
            is_complete = analyze_conversation_completion(last_message)
            
            export_data.append({
                'Chat ID': conv['chatid'],
                'Date début': conv['start_time'],
                'Date fin': conv['end_time'],
                'Nombre total messages': conv['message_count'],
                'Messages client': conv['customer_messages'],
                'Messages agent': conv['agent_messages'],
                'Conversation complète': 'Oui' if is_complete else 'Non',
                'Résumé LLM': summary
            })
    
    export_df = pd.DataFrame(export_data)
    
    # Créer le fichier CSV
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_data = csv_buffer.getvalue()
    
    # Bouton de téléchargement
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_data,
        file_name=f"conversations_cci_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def run_bulk_analysis(conversations_df):
    """
    Lancer une analyse complète en masse
    """
    st.info("Cette fonctionnalité générera des résumés LLM pour toutes les conversations. Cela peut prendre plusieurs minutes.")
    
    if st.button("▶️ Confirmer l'analyse en masse"):
        generate_all_summaries(conversations_df)
