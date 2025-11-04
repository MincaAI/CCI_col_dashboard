"""
Requêtes SQL pour le dashboard CCI Colombia
"""
import os
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from database.connection import execute_query

def get_conversations_in_period(start_date, end_date):
    """
    Récupérer toutes les conversations dans une période donnée
    """
    query = """
    SELECT DISTINCT chatid::text as chatid, 
           MIN(created_at) as start_time,
           MAX(created_at) as end_time,
           COUNT(*) as message_count
    FROM public.message 
    WHERE created_at >= %s AND created_at <= %s
    GROUP BY chatid
    ORDER BY start_time DESC
    """
    return execute_query(query, (start_date, end_date))

def get_conversation_messages(chatid):
    """
    Récupérer tous les messages d'une conversation spécifique
    """
    query = """
    SELECT messageid::text as messageid, chatid::text as chatid, content, role, created_at
    FROM public.message 
    WHERE chatid::text = %s
    ORDER BY created_at ASC
    """
    return execute_query(query, (chatid,))

def get_kpi_data(start_date, end_date):
    """
    Récupérer les données pour les KPIs
    """
    # Nombre total d'utilisateurs (conversations uniques)
    users_query = """
    SELECT COUNT(DISTINCT chatid) as total_users
    FROM public.message 
    WHERE created_at >= %s AND created_at <= %s
    """
    
    # Longueur moyenne des conversations
    avg_length_query = """
    SELECT AVG(message_count) as avg_conversation_length
    FROM (
        SELECT chatid, COUNT(*) as message_count
        FROM public.message 
        WHERE created_at >= %s AND created_at <= %s
        GROUP BY chatid
    ) as conv_stats
    """
    
    # Nouvelles conversations par jour
    daily_conversations_query = """
    SELECT DATE(start_time) as date, COUNT(*) as new_conversations
    FROM (
        SELECT chatid, MIN(created_at) as start_time
        FROM public.message 
        WHERE created_at >= %s AND created_at <= %s
        GROUP BY chatid
    ) as conversation_starts
    GROUP BY DATE(start_time)
    ORDER BY date
    """
    
    users_df = execute_query(users_query, (start_date, end_date))
    avg_length_df = execute_query(avg_length_query, (start_date, end_date))
    daily_conversations_df = execute_query(daily_conversations_query, (start_date, end_date))
    
    return {
        'total_users': users_df.iloc[0]['total_users'] if not users_df.empty else 0,
        'avg_conversation_length': round(avg_length_df.iloc[0]['avg_conversation_length'], 1) if not avg_length_df.empty else 0,
        'daily_conversations': daily_conversations_df
    }

def get_completion_candidates(start_date, end_date):
    """
    Récupérer toutes les conversations pour l'analyse de completion
    """
    query = """
    SELECT DISTINCT chatid::text as chatid,
           MIN(created_at) as start_time,
           MAX(created_at) as end_time,
           COUNT(*) as message_count
    FROM public.message 
    WHERE created_at >= %s AND created_at <= %s
    GROUP BY chatid
    ORDER BY MAX(created_at) DESC
    """
    return execute_query(query, (start_date, end_date))

def get_completion_stats(start_date, end_date):
    """
    Récupérer les statistiques de completion depuis la table conversation_analysis
    """
    query = """
    SELECT 
        COUNT(*) as total_conversations,
        COUNT(CASE WHEN ca.is_completed = true THEN 1 END) as completed_count,
        COUNT(CASE WHEN ca.is_completed = false THEN 1 END) as incomplete_count,
        COUNT(CASE WHEN ca.is_completed IS NULL THEN 1 END) as not_analyzed_count
    FROM (
        SELECT DISTINCT m.chatid
        FROM public.message m
        WHERE m.created_at >= %s AND m.created_at <= %s
    ) as conversations
    LEFT JOIN conversation_analysis ca ON conversations.chatid::text = ca.chatid::text
    """
    return execute_query(query, (start_date, end_date))

def get_engaged_conversations_count(start_date, end_date):
    """
    Récupérer le nombre de conversations engagées (> 2 messages)
    """
    query = """
    SELECT COUNT(*) as engaged_conversations
    FROM (
        SELECT chatid, COUNT(*) as message_count
        FROM public.message 
        WHERE created_at >= %s AND created_at <= %s
        GROUP BY chatid
        HAVING COUNT(*) > 2
    ) as engaged
    """
    return execute_query(query, (start_date, end_date))

def get_conversations_summary_data(start_date, end_date):
    """
    Récupérer les données pour le tableau de résumé des conversations avec analyses IA
    """
    query = """
    SELECT m.chatid::text as chatid,
           MIN(m.created_at) as start_time,
           MAX(m.created_at) as end_time,
           COUNT(*) as message_count,
           COUNT(CASE WHEN m.role = 'customer' THEN 1 END) as customer_messages,
           COUNT(CASE WHEN m.role = 'agent' THEN 1 END) as agent_messages,
           c.value as whatsapp_number,
           COALESCE(w.nombre, 'Inconnu') as prenom,
           COALESCE(w.apellido, '') as nom,
           COALESCE(w.empresa, 'Non spécifié') as entreprise,
           -- Données d'analyse IA depuis conversation_analysis
           ca.client_name as client_name_ai,
           ca.company_name as company_name_ai,
           ca.conversation_summary,
           ca.service_interest,
           ca.is_completed,
           ca.analysis_date
    FROM public.message m
    LEFT JOIN public.chat c ON m.chatid = c.chatid
    LEFT JOIN public.whatsapp_numbers w ON '+' || c.value = w.celular
    LEFT JOIN conversation_analysis ca ON m.chatid::text = ca.chatid::text
    WHERE m.created_at >= %s AND m.created_at <= %s
    GROUP BY m.chatid, c.value, w.nombre, w.apellido, w.empresa, 
             ca.client_name, ca.company_name, ca.conversation_summary, ca.service_interest, ca.is_completed, ca.analysis_date
    ORDER BY MAX(m.created_at) DESC
    """
    conversations_df = execute_query(query, (start_date, end_date))
    
    # Créer les colonnes finales en combinant données manuelles et IA
    if not conversations_df.empty:
        conversations_df['client_name_final'] = conversations_df.apply(
            lambda row: (row['client_name_ai'] if pd.notna(row['client_name_ai']) and row['client_name_ai'] != '' 
                        else (f"{row['prenom']} {row['nom']}".strip() if row['prenom'] != 'Inconnu' 
                             else '-')), axis=1
        )
        
        conversations_df['company_name_final'] = conversations_df.apply(
            lambda row: (row['company_name_ai'] if pd.notna(row['company_name_ai']) and row['company_name_ai'] != '' 
                        else (row['entreprise'] if row['entreprise'] != 'Non spécifié' 
                             else '-')), axis=1
        )
    
    return conversations_df

def get_all_conversations_with_analysis():
    """
    Récupérer toutes les conversations avec leurs analyses pour le sélecteur
    """
    query = """
    SELECT DISTINCT
        m.chatid::text as chatid,
        MAX(m.created_at) as last_activity,
        COUNT(*) as message_count,
        -- Nom d'affichage du client
        CASE 
            WHEN ca.client_name IS NOT NULL AND ca.client_name != '' THEN ca.client_name
            WHEN w.nombre != 'Inconnu' AND w.nombre IS NOT NULL THEN TRIM(CONCAT(w.nombre, ' ', COALESCE(w.apellido, '')))
            ELSE 'Contact anonyme'
        END as display_name,
        -- Numéro WhatsApp
        COALESCE(c.value, 'Non disponible') as whatsapp_number,
        -- Entreprise
        CASE 
            WHEN ca.company_name IS NOT NULL AND ca.company_name != '' THEN ca.company_name
            WHEN w.empresa IS NOT NULL AND w.empresa != 'Non spécifié' THEN w.empresa
            ELSE 'Non spécifié'
        END as company_name,
        -- Résumé court pour aperçu
        CASE 
            WHEN ca.conversation_summary IS NOT NULL THEN LEFT(ca.conversation_summary, 100) || '...'
            ELSE 'Résumé non disponible'
        END as summary_preview
    FROM public.message m
    LEFT JOIN public.chat c ON m.chatid = c.chatid
    LEFT JOIN public.whatsapp_numbers w ON '+' || c.value = w.celular
    LEFT JOIN conversation_analysis ca ON m.chatid = ca.chatid
    GROUP BY m.chatid, c.value, w.nombre, w.apellido, w.empresa, 
             ca.client_name, ca.company_name, ca.conversation_summary
    ORDER BY MAX(m.created_at) DESC
    """
    return execute_query(query)
