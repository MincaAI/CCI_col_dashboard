"""
Composants de la section conversations
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import io

# Charger les variables d'environnement
load_dotenv()

from database.queries import get_conversations_summary_data, get_conversation_messages, get_all_conversations_with_analysis
from utils.llm_analysis import analyze_conversation_completion, regenerate_summary_only, regenerate_all_summaries
from config.settings import MARIA_THEMES

def show_conversations_section(start_date, end_date):
    """
    Afficher la section conversations du dashboard
    """
    st.header("Conversations et Analyses")
    
    # DEBUG : Afficher les paramètres de recherche
    st.write(f"🔍 **Debug** - Recherche de conversations entre {start_date} et {end_date}")
    
    # Récupérer les données des conversations
    with st.spinner("Chargement des conversations..."):
        conversations_df = get_conversations_summary_data(start_date, end_date)
    
    # DEBUG : Afficher le résultat de la requête
    st.write(f"📊 **Debug** - Nombre de conversations trouvées: {len(conversations_df)}")
    st.write(f"📊 **Debug** - DataFrame vide? {conversations_df.empty}")
    
    if not conversations_df.empty:
        st.write(f"📊 **Debug** - Colonnes: {list(conversations_df.columns)}")
        st.write(f"📊 **Debug** - Premières lignes:")
        st.dataframe(conversations_df.head(2))
    
    if conversations_df.empty:
        st.info("Aucune conversation trouvée pour cette période.")
        
        # Essayer une requête simplifiée pour debug
        st.write("🔍 Test d'une requête simplifiée...")
        from database.connection import execute_query
        test_query = """
        SELECT COUNT(DISTINCT chatid) as nb_conversations
        FROM public.message 
        WHERE created_at >= %s AND created_at <= %s
        """
        test_result = execute_query(test_query, (start_date, end_date))
        if not test_result.empty:
            st.write(f"✅ Requête simplifiée trouve: {test_result.iloc[0]['nb_conversations']} conversations")
        else:
            st.write("❌ Même la requête simplifiée échoue")
        return
    
    # Onglets pour différentes vues
    tab1, tab2 = st.tabs(["📊 Tableau résumé", "🔍 Lecteur de conversations"])
    
    with tab1:
        # Section de contrôle des résumés
        show_summary_control_section(conversations_df)
        
        # Tableau des conversations avec pagination
        show_conversations_table(conversations_df)
        
        # Section d'analyse détaillée
        st.markdown("---")
        show_detailed_analysis_section(conversations_df)
    
    with tab2:
        # Nouvelle section lecteur de conversations
        show_conversation_reader_section()

def show_conversations_table(conversations_df):
    """
    Afficher le tableau des conversations avec pagination
    """
    
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
    
    # Configuration des colonnes - focus MAXIMUM sur le résumé
    column_config = {
        "Contact": st.column_config.TextColumn("Contact", width=120),
        "Nom": st.column_config.TextColumn("Nom", width=100),
        "Entreprise": st.column_config.TextColumn("Entreprise", width=100),
        "Messages": st.column_config.NumberColumn("Messages", width=80),  # Très étroit pour les nombres
        "Dernière activité": st.column_config.DatetimeColumn("Dernière activité", format="DD/MM/YYYY HH:mm", width=130),
        "Service d'intérêt": st.column_config.TextColumn("Service d'intérêt", width=150),
        "Résumé": st.column_config.TextColumn("Résumé", width=800)  # Largeur augmentée pour voir plus de contenu
    }
    
    # Afficher le tableau avec plus de hauteur pour voir les résumés complets
    event = st.dataframe(
        display_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,  # Utiliser toute la largeur disponible
        height=600,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Actions sur la sélection
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        # CORRECTION : Utiliser display_df pour récupérer les données affichées
        selected_display_row = display_df.iloc[selected_idx]
        
        # Récupérer le chatid et retrouver la ligne complète dans page_df
        # Le chatid n'est pas affiché mais on peut le récupérer via l'index
        selected_chatid = page_df.iloc[selected_idx]['chatid']
        selected_row = page_df.iloc[selected_idx]

        # Afficher le résumé complet en premier
        st.markdown("---")
        st.subheader("Résumé complet de la conversation")
        
        # Informations de base
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Contact", selected_row.get('whatsapp_number', 'N/A'))
        with col2:
            st.metric("Messages", selected_row.get('message_count', 'N/A'))
        with col3:
            st.metric("Service d'intérêt", selected_row.get('service_interest', 'Non analysé'))
        
        # DEBUG : Afficher les sources de données
        st.write("🔍 **DEBUG - Sources de données:**")
        st.write(f"- selected_idx: {selected_idx}")
        st.write(f"- Résumé dans page_df: {len(str(selected_row.get('conversation_summary', ''))) if selected_row.get('conversation_summary') else 0} caractères")
        
        # Récupérer DIRECTEMENT depuis la base pour être sûr
        from database.connection import execute_query
        summary_query = """
        SELECT conversation_summary 
        FROM conversation_analysis 
        WHERE chatid::text = %s
        """
        summary_result = execute_query(summary_query, (selected_chatid,))
        
        if not summary_result.empty and pd.notna(summary_result.iloc[0]['conversation_summary']):
            db_summary = summary_result.iloc[0]['conversation_summary']
            st.write(f"- Résumé DIRECT depuis PostgreSQL: {len(str(db_summary))} caractères")
            
            st.subheader("Résumé complet de la conversation")
            st.text_area("", 
                        value=str(db_summary), 
                        height=400, 
                        disabled=True,
                        label_visibility="collapsed")
        else:
            st.info("Aucun résumé disponible pour cette conversation dans PostgreSQL")
        
        # Section pour voir les messages complets
        with st.expander("Voir les messages complets"):
            show_conversation_details(selected_chatid)

def prepare_display_dataframe(conversations_df):
    """
    Préparer le DataFrame pour l'affichage dans le tableau - utilise les données PostgreSQL
    """
    display_df = conversations_df.copy()
    
    # Trier par dernière activité (plus récent en premier)
    display_df = display_df.sort_values('end_time', ascending=False)
    
    # Convertir UUID en string pour éviter les erreurs Arrow
    display_df['chatid'] = display_df['chatid'].astype(str)
    
    # 1. CONTACT (numéro WhatsApp)
    def get_contact_display(row):
        if pd.notna(row['whatsapp_number']):
            return f"+{row['whatsapp_number']}"
        return "Non disponible"
    
    display_df['contact_display'] = display_df.apply(get_contact_display, axis=1)
    
    # 2. NOM (utilise client_name_final de la base)
    display_df['nom_display'] = display_df['client_name_final']
    
    # 3. ENTREPRISE (utilise company_name_final de la base)
    display_df['entreprise_display'] = display_df['company_name_final']
    
    # 4. RÉSUMÉ (depuis la base PostgreSQL) - Version COMPLÈTE pour l'affichage
    def get_conversation_summary_display(row):
        if pd.notna(row['conversation_summary']) and row['conversation_summary']:
            # GARDER le résumé COMPLET pour l'affichage
            return row['conversation_summary']
        return "⏳ Non généré"
    
    display_df['resume_display'] = display_df.apply(get_conversation_summary_display, axis=1)
    
    # 5. SERVICE D'INTÉRÊT (depuis la base PostgreSQL)
    def get_service_interest(row):
        if pd.notna(row['service_interest']) and row['service_interest']:
            return row['service_interest']
        return "⏳ Non analysé"
    
    display_df['service_display'] = display_df.apply(get_service_interest, axis=1)
    
    # Renommer TOUTES les colonnes en une seule fois
    display_df = display_df.rename(columns={
        'contact_display': 'Contact',
        'nom_display': 'Nom',
        'entreprise_display': 'Entreprise',
        'message_count': 'Messages',
        'end_time': 'Dernière activité',
        'resume_display': 'Résumé',
        'service_display': 'Service d\'intérêt'
    })
    
    # Retourner seulement les colonnes voulues
    return display_df[['Contact', 'Nom', 'Entreprise', 'Messages', 'Dernière activité', 'Service d\'intérêt', 'Résumé']]

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
    
    # Afficher seulement les messages
    show_conversation_messages(messages_df)

def show_conversation_messages(messages_df):
    """
    Afficher les messages de la conversation
    """
    st.markdown("### Messages de la conversation")
    
    for _, message in messages_df.iterrows():
        if message['role'] == 'agent':
            # Message de l'agent (MarIA) - couleur grise
            st.markdown(f"""
            <div style="background-color: #F5F5F5; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #999999;">
                <strong>Agent MarIA</strong> <span style="color: #666; font-size: 0.8em;">{message['created_at']}</span><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Message du client - couleur blanche
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #CCCCCC; border: 1px solid #E0E0E0;">
                <strong>Client</strong> <span style="color: #666; font-size: 0.8em;">{message['created_at']}</span><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)


def show_detailed_analysis_section(conversations_df):
    """
    Afficher la section d'analyse détaillée
    """
    st.subheader("Export")
    
    if st.button("Exporter le tableau", use_container_width=True):
        export_conversations_data(conversations_df)

def show_summary_control_section(conversations_df):
    """
    Afficher le résumé des conversations (section simplifiée)
    """
    total_conversations = len(conversations_df)
    
    # Compter les conversations avec analyses IA depuis la base
    analyzed_conversations = len(conversations_df[conversations_df['conversation_summary'].notna() & 
                                                 (conversations_df['conversation_summary'] != '')])
    
    st.metric("Total conversations", total_conversations)
    
    # Message informatif pour la génération
    if analyzed_conversations < total_conversations:
        missing_count = total_conversations - analyzed_conversations
        st.info(f"""
        💡 **{missing_count} conversation(s) en attente d'analyse IA**
        
        Pour générer les résumés et extractions manquants, utilisez le script batch :
        ```bash
        python scripts/generate_analysis_batch.py --limit {missing_count} --days 30
        ```
        """)
    
    st.markdown("---")



def show_conversation_reader_section():
    """
    Section pour sélectionner et lire une conversation complète
    """
    st.subheader("🔍 Lecteur de conversations")
    st.markdown("Sélectionnez un contact pour lire sa conversation complète avec l'agent IA.")
    
    # Récupérer toutes les conversations
    with st.spinner("Chargement de la liste des conversations..."):
        all_conversations = get_all_conversations_with_analysis()
    
    if all_conversations.empty:
        st.info("Aucune conversation disponible.")
        return
    
    # Sélecteur de conversation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Créer les options du selectbox avec numéro de téléphone
        conversation_options = []
        for _, conv in all_conversations.iterrows():
            # Format: "+Numéro - Nom (Entreprise) - Date"
            display_text = f"+{conv['whatsapp_number']}"
            if conv['display_name'] != 'Contact anonyme':
                display_text += f" - {conv['display_name']}"
            if conv['company_name'] != 'Non spécifié':
                display_text += f" ({conv['company_name']})"
            display_text += f" - {conv['last_activity'].strftime('%d/%m/%Y')}"
            conversation_options.append((display_text, conv['chatid']))
        
        if conversation_options:
            selected_conversation = st.selectbox(
                "Choisir une conversation:",
                options=conversation_options,
                format_func=lambda x: x[0],
                key="conversation_selector"
            )
            
            selected_chatid = selected_conversation[1] if selected_conversation else None
        else:
            selected_chatid = None
    
    with col2:
        if selected_chatid:
            # Afficher les infos du contact sélectionné
            selected_info = all_conversations[all_conversations['chatid'] == selected_chatid].iloc[0]
            st.info(f"""
            **Contact sélectionné:**
            - 👤 {selected_info['display_name']}
            - 🏢 {selected_info['company_name']}
            - 📱 +{selected_info['whatsapp_number']}
            - 📊 {selected_info['message_count']} messages
            - 📅 {selected_info['last_activity'].strftime('%d/%m/%Y %H:%M')}
            """)
    
    # Afficher la conversation si sélectionnée
    if selected_chatid:
        st.markdown("---")
        show_full_conversation_details(selected_chatid)

def show_full_conversation_details(chatid):
    """
    Afficher les détails complets d'une conversation sélectionnée
    """
    # Récupérer les messages de la conversation
    with st.spinner("Chargement de la conversation..."):
        messages_df = get_conversation_messages(chatid)
    
    if messages_df.empty:
        st.error("Impossible de récupérer les messages de cette conversation.")
        return
    
    # Récupérer l'analyse si disponible
    all_conversations = get_all_conversations_with_analysis()
    conversation_info = all_conversations[all_conversations['chatid'] == chatid]
    
    if not conversation_info.empty:
        conv_info = conversation_info.iloc[0]
        
        # Afficher un résumé en haut
        if conv_info['summary_preview'] != 'Résumé non disponible':
            with st.expander("Résumé de la conversation", expanded=False):
                # Récupérer le résumé complet depuis la base
                summary_query = """
                SELECT conversation_summary 
                FROM conversation_analysis 
                WHERE chatid::text = %s
                """
                from database.connection import execute_query
                summary_result = execute_query(summary_query, (chatid,))
                
                if not summary_result.empty and pd.notna(summary_result.iloc[0]['conversation_summary']):
                    st.markdown(summary_result.iloc[0]['conversation_summary'])
                else:
                    st.info("Résumé non disponible pour cette conversation.")
    
    # Afficher la conversation
    st.subheader("Messages de la conversation")
    
    # Container pour les messages avec scroll
    message_container = st.container()
    
    with message_container:
        for _, message in messages_df.iterrows():
            if message['role'] == 'agent':
                # Message de l'agent (MarIA) - couleur grise
                st.markdown(f"""
                <div style="
                    background-color: #F5F5F5;
                    padding: 15px;
                    border-radius: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #999999;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <strong style="color: #333;">Agent MarIA</strong>
                        <span style="color: #666; font-size: 0.8em; margin-left: 10px;">
                            {message['created_at'].strftime('%d/%m/%Y %H:%M:%S')}
                        </span>
                    </div>
                    <div style="color: #333; line-height: 1.4;">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Message du client - couleur blanche
                st.markdown(f"""
                <div style="
                    background-color: #FFFFFF;
                    padding: 15px;
                    border-radius: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #CCCCCC;
                    border: 1px solid #E0E0E0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-left: 20px;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <strong style="color: #333;">Client</strong>
                        <span style="color: #666; font-size: 0.8em; margin-left: 10px;">
                            {message['created_at'].strftime('%d/%m/%Y %H:%M:%S')}
                        </span>
                    </div>
                    <div style="color: #333; line-height: 1.4;">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Statistiques de la conversation
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    total_messages = len(messages_df)
    client_messages = len(messages_df[messages_df['role'] == 'customer'])
    agent_messages = len(messages_df[messages_df['role'] == 'agent'])
    duration = messages_df['created_at'].max() - messages_df['created_at'].min()
    
    with col1:
        st.metric("Messages total", total_messages)
    with col2:
        st.metric("Messages client", client_messages)
    with col3:
        st.metric("Messages agent", agent_messages)
    with col4:
        duration_str = f"{duration.days}j {duration.seconds//3600}h {(duration.seconds//60)%60}m"
        st.metric("Durée", duration_str)

def export_conversations_data(conversations_df):
    """
    Exporter le tableau affiché des conversations au format CSV
    """
    # Préparer les données exactement comme dans le tableau affiché
    display_df = prepare_display_dataframe(conversations_df)
    
    # Créer le fichier CSV
    csv_buffer = io.StringIO()
    display_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_data = csv_buffer.getvalue()
    
    # Bouton de téléchargement
    st.download_button(
        label="📥 Télécharger le tableau CSV",
        data=csv_data,
        file_name=f"conversations_tableau_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

