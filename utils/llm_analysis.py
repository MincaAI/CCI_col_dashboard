"""
Module d'analyse LLM pour les résumés de conversations
"""
import openai
import streamlit as st
from config.settings import OPENAI_API_KEY, MARIA_THEMES
import json

# Configuration OpenAI
openai.api_key = OPENAI_API_KEY

def analyze_conversation_completion(last_message_content):
    """
    Analyser si une conversation est complète (contient un numéro WhatsApp)
    """
    try:
        prompt = f"""
        Analyse ce message final d'une conversation avec l'agent MarIA de la CCI France Colombia.
        
        Message: "{last_message_content}"
        
        Détermine si cette conversation est COMPLÈTE selon ces critères:
        1. Le message contient un numéro de téléphone WhatsApp (format +57 xxx xxx xxxx)
        2. Le message indique une redirection vers un contact spécifique de l'équipe CCI
        
        Réponds uniquement par "COMPLÈTE" ou "INCOMPLÈTE".
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        return "COMPLÈTE" in result.upper()
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de completion: {e}")
        return False

def generate_conversation_summary(messages_df):
    """
    Générer un résumé structuré d'une conversation
    """
    try:
        # Construire le contexte de la conversation
        conversation_text = ""
        for _, msg in messages_df.iterrows():
            role = "Agent MarIA" if msg['role'] == 'agent' else "Client"
            conversation_text += f"{role}: {msg['content']}\n"
        
        prompt = f"""
        Analyse cette conversation entre l'agent MarIA (assistant virtuel de la CCI France Colombia) et un client.
        
        CONVERSATION:
        {conversation_text}
        
        Génère un résumé structuré en français avec ces sections:
        
        1. PROFIL CLIENT (2-3 phrases sur qui est le client et son secteur)
        2. BESOINS IDENTIFIÉS (liste des besoins principaux exprimés)
        3. SERVICES RECOMMANDÉS (services CCI mentionnés ou recommandés)
        4. STATUT (conversation complète/incomplète et pourquoi)
        5. POINTS CLÉS (3-4 points importants à retenir)
        
        Sois concis et professionnel. Limite chaque section à 2-3 lignes maximum.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du résumé: {e}")
        return "Résumé non disponible"

def extract_themes_analysis(messages_df):
    """
    Analyser quels thèmes MarIA ont été couverts dans la conversation
    """
    try:
        conversation_text = ""
        for _, msg in messages_df.iterrows():
            if msg['role'] == 'agent':  # Seulement les messages de MarIA
                conversation_text += f"{msg['content']}\n"
        
        themes_list = "\n".join([f"{i+1}. {theme}" for i, theme in enumerate(MARIA_THEMES)])
        
        prompt = f"""
        Analyse les messages de l'agent MarIA pour identifier quels thèmes ont été abordés.
        
        THÈMES DE MARÌA:
        {themes_list}
        
        MESSAGES DE MARÌA:
        {conversation_text}
        
        Pour chaque thème, réponds par "OUI" ou "NON" selon s'il a été abordé:
        
        Format de réponse:
        1. Utilisation actuelle des services: [OUI/NON]
        2. Expérience avec les services: [OUI/NON]
        3. Objectif principal en Colombie: [OUI/NON]
        4. Attentes d'accompagnement: [OUI/NON]
        5. Perception de valeur de la CCI: [OUI/NON]
        6. Suggestions d'amélioration: [OUI/NON]
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse des thèmes: {e}")
        return "Analyse non disponible"
