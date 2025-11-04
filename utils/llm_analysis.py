"""
Module d'analyse LLM pour les résumés de conversations
"""
import os
import sys
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import json

# Forcer l'encodage UTF-8 pour tout le script
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Charger les variables d'environnement
load_dotenv()

from config.settings import OPENAI_API_KEY, MARIA_THEMES

# Configuration OpenAI - Nouveau client avec headers ASCII
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={
        "User-Agent": "CCI-Colombia-Dashboard/1.0"
    }
)

def ensure_utf8(text):
    """S'assurer qu'une chaîne est en UTF-8"""
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='ignore')
    return str(text).encode('utf-8', errors='ignore').decode('utf-8')

def analyze_conversation_completion(messages_content):
    """
    Analyser si une conversation est complète (contient une recommandation de service)
    """
    try:
        # Analyser tous les messages de MarIA, pas seulement le dernier
        conversation_text = ""
        if isinstance(messages_content, str):
            # Si c'est juste le dernier message (ancien comportement)
            conversation_text = messages_content
        else:
            # Si c'est une liste de messages (nouveau comportement)
            for msg in messages_content:
                if msg.get('role') == 'agent':  # Seulement les messages de MarIA
                    conversation_text += f"{msg['content']}\n"
        
        prompt = f"""
        Analyse cette conversation avec l'agent MarIA de la CCI France Colombia pour déterminer si elle est COMPLÈTE.
        
        MESSAGES DE MARIA:
        {conversation_text}
        
        Une conversation est COMPLÈTE si MarIA a fait au moins UNE des actions suivantes:
        1. Recommandé un service CCI spécifique
        2. Fourni un contact (nom + numéro WhatsApp)
        3. Orienté vers une personne de l'équipe CCI
        4. Donné des informations concrètes sur un service
        5. Fourni des liens utiles (réseaux sociaux, newsletter, etc.)
        
        Une conversation est INCOMPLÈTE si MarIA a seulement:
        - Salué le client
        - Posé des questions de qualification
        - Demandé des précisions
        - Donné des informations générales sur la CCI
        
        Exemples de messages COMPLETS (recommandations):
        - "Je vous mets en contact avec Yasmine au +57 304 658 9045"
        - "Pour l'accompagnement commercial, contactez Nicolas Velásquez"
        - "Je vous recommande notre service de missions économiques"
        - "Voici nos réseaux sociaux pour suivre nos événements"
        - "Vous pouvez vous inscrire à notre newsletter"
        
        Exemples de messages INCOMPLETS:
        - "Bonjour ! Pour mieux vous aider..."
        - "Pourriez-vous me préciser votre secteur d'activité ?"
        - "Ravie de vous accueillir dans notre communauté"
        
        Réponds uniquement par "COMPLÈTE" ou "INCOMPLÈTE".
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        return "COMPLÈTE" in result.upper()
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de l'analyse de completion: {e}")
        return False

def generate_conversation_summary(messages_df):
    """
    Générer un résumé structuré d'une conversation
    """
    try:
        # Limiter aux 20 premiers messages pour économiser des tokens
        limited_df = messages_df.head(20)
        
        # Construire le contexte de la conversation (limité)
        conversation_text = ""
        for _, msg in limited_df.iterrows():
            role = "Agent" if msg['role'] == 'agent' else "Client"
            # Limiter chaque message à 300 caractères
            content = str(msg['content'])[:300]
            conversation_text += f"{role}: {content}\n"
        
        # Prompt ultra-court pour économiser
        prompt = f"""Conversation CCI:
{conversation_text}

Resume en 3 points courts (meme langue que conversation):
1. Besoins du membre
2. Services/contacts recommandes
3. Statut"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,  # Réduit de 300 à 150 pour économiser
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de la génération du résumé: {e}")
        return "Résumé non disponible"

def extract_client_name_from_conversation(messages_df):
    """
    Extraire le nom du client depuis les messages de la conversation
    """
    try:
        conversation_text = ""
        for _, msg in messages_df.iterrows():
            conversation_text += f"{'Client' if msg['role'] == 'customer' else 'MarIA'}: {msg['content']}\n"
        
        prompt = f"""
        Analyse cette conversation entre MarIA (agent CCI) et un client pour identifier le NOM du client.
        
        CONVERSATION:
        {conversation_text}
        
        Trouve le nom/prénom du client mentionné dans la conversation.
        
        Règles:
        - Cherche quand le client se présente ou donne son nom
        - Cherche quand MarIA utilise le nom du client
        - Si tu trouves un nom, réponds SEULEMENT le prénom (ou prénom + nom)
        - Si pas de nom trouvé, réponds exactement "INCONNU"
        
        Réponse (juste le nom):
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        return result if result != "INCONNU" else None
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de l'extraction du nom: {e}")
        return None

def extract_company_from_conversation(messages_df):
    """
    Extraire le nom de l'entreprise depuis les messages de la conversation
    """
    try:
        conversation_text = ""
        for _, msg in messages_df.iterrows():
            conversation_text += f"{'Client' if msg['role'] == 'customer' else 'MarIA'}: {msg['content']}\n"
        
        prompt = f"""
        Analyse cette conversation entre MarIA (agent CCI) et un client pour identifier le NOM DE L'ENTREPRISE du client.
        
        CONVERSATION:
        {conversation_text}
        
        Trouve le nom de l'entreprise/société du client mentionné dans la conversation.
        
        Règles:
        - Cherche quand le client mentionne son entreprise, société, compagnie
        - Cherche les noms d'entreprises dans le contexte professionnel
        - Si tu trouves un nom d'entreprise, réponds SEULEMENT le nom (sans "Entreprise:", "Société:", etc.)
        - Si pas d'entreprise trouvée, réponds exactement "Non spécifié"
        
        Réponse (juste le nom de l'entreprise):
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,  # Réduit de 30 à 20
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        return result if result != "Non spécifié" else None
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de l'extraction de l'entreprise: {e}")
        return None

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
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de l'analyse des thèmes: {e}")
        return "Analyse non disponible"

def regenerate_summary_only(chatid):
    """
    Re-générer uniquement le résumé d'une conversation existante
    """
    try:
        from database.queries import get_conversation_messages
        from database.connection import execute_query
        
        # Récupérer les messages de la conversation
        messages_df = get_conversation_messages(chatid)
        if messages_df.empty:
            return False, "Aucun message trouvé"
        
        # Générer le nouveau résumé avec le prompt mis à jour
        new_summary = generate_conversation_summary(messages_df)
        if not new_summary:
            return False, "Erreur lors de la génération du résumé"
        
        # Mettre à jour uniquement le résumé en base
        update_query = """
        UPDATE conversation_analysis 
        SET conversation_summary = %s, 
            last_updated = CURRENT_TIMESTAMP
        WHERE chatid::text = %s
        """
        
        result = execute_query(update_query, (new_summary, chatid), fetch=False)
        if result is not None:
            return True, new_summary
        else:
            return False, "Erreur lors de la mise à jour en base"
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de la re-génération: {e}")
        return False, str(e)

def regenerate_all_summaries(start_date=None, end_date=None, limit=None):
    """
    Re-générer tous les résumés existants avec le nouveau prompt
    """
    try:
        from database.connection import execute_query
        
        # Construire la requête pour récupérer les conversations à re-générer
        base_query = """
        SELECT DISTINCT ca.chatid::text as chatid 
        FROM conversation_analysis ca
        """
        
        conditions = []
        params = []
        
        if start_date and end_date:
            conditions.append("ca.conversation_start_date >= %s AND ca.conversation_end_date <= %s")
            params.extend([start_date, end_date])
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY ca.conversation_end_date DESC"
        
        if limit:
            base_query += f" LIMIT {limit}"
        
        # Récupérer les conversations
        conversations_df = execute_query(base_query, params if params else None)
        
        if conversations_df.empty:
            return {"success": 0, "errors": 0, "total": 0}
        
        results = {"success": 0, "errors": 0, "total": len(conversations_df)}
        
        # Re-générer chaque résumé
        for _, row in conversations_df.iterrows():
            chatid = row['chatid']
            success, message = regenerate_summary_only(chatid)
            
            if success:
                results["success"] += 1
                print(f"✅ Résumé re-généré pour {chatid}")
            else:
                results["errors"] += 1
                print(f"❌ Erreur pour {chatid}: {message}")
            
            # Pause pour éviter de surcharger l'API
            import time
            time.sleep(1)
        
        return results
        
    except Exception as e:
        # Éviter st.error() qui cause des problèmes UTF-8 hors contexte Streamlit
        print(f"Erreur lors de la re-génération en batch: {e}")
        return {"success": 0, "errors": 1, "total": 0}

def analyze_service_interest(messages_df):
    """
    Analyser les services CCI qui intéressent le client depuis une conversation
    """
    if messages_df.empty:
        return "Information générale"
    
    # Préparer les messages pour l'analyse
    conversation_text = ""
    for _, message in messages_df.iterrows():
        role = "Client" if message['role'] == 'customer' else "Agent"
        conversation_text += f"{role}: {message['content']}\n\n"
    
    prompt = f"""
    Analyse cette conversation pour identifier quel service de la Chambre de Commerce et d'Industrie (CCI) France-Colombie intéresse le plus ce client.

    CONVERSATION:
    {conversation_text}

    SERVICES CCI DISPONIBLES:
    1. Accompagnement commercial - Aide au développement commercial, recherche de partenaires
    2. Missions économiques - Participation à des missions commerciales, salons
    3. Networking et événements - Participation à des événements de networking
    4. Formation et certification - Formations professionnelles, certifications
    5. Conseil juridique - Accompagnement juridique, réglementaire
    6. Études de marché - Analyses sectorielles, études économiques
    7. Implantation d'entreprise - Aide à l'installation en France ou Colombie
    8. Communication et visibilité - Promotion d'entreprise, communication
    9. Services administratifs - Aide administrative, formalités
    10. Information générale - Demandes d'information générales

    INSTRUCTIONS:
    1. Identifie le service CCI qui correspond le mieux aux besoins/intérêts exprimés
    2. Base-toi sur les questions, demandes et sujets abordés par le client
    3. Retourne SEULEMENT le nom du service principal, sans explication
    4. Si aucun service spécifique n'est identifiable, retourne "Information générale"

    RÉPONSE (nom du service seulement):
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],  # Pas de system message
            max_tokens=30,
            temperature=0
        )
        
        service_interest = response.choices[0].message.content.strip()
        return service_interest if service_interest else "Information générale"
        
    except Exception as e:
        print(f"Erreur lors de l'analyse du service d'intérêt: {e}")
        return "Information générale"
