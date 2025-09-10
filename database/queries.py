"""
Requêtes SQL pour le dashboard CCI Colombia
"""
from datetime import datetime, timedelta
import pandas as pd
from database.connection import execute_query

def get_conversations_in_period(start_date, end_date):
    """
    Récupérer toutes les conversations dans une période donnée
    """
    query = """
    SELECT DISTINCT chatid, 
           MIN(created_at) as start_time,
           MAX(created_at) as end_time,
           COUNT(*) as message_count
    FROM public.messages 
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
    SELECT messageid, chatid, content, role, created_at
    FROM public.messages 
    WHERE chatid = %s
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
    FROM public.messages 
    WHERE created_at >= %s AND created_at <= %s
    """
    
    # Longueur moyenne des conversations
    avg_length_query = """
    SELECT AVG(message_count) as avg_conversation_length
    FROM (
        SELECT chatid, COUNT(*) as message_count
        FROM public.messages 
        WHERE created_at >= %s AND created_at <= %s
        GROUP BY chatid
    ) as conv_stats
    """
    
    # Messages par jour
    daily_messages_query = """
    SELECT DATE(created_at) as date, COUNT(*) as message_count
    FROM public.messages 
    WHERE created_at >= %s AND created_at <= %s
    GROUP BY DATE(created_at)
    ORDER BY date
    """
    
    users_df = execute_query(users_query, (start_date, end_date))
    avg_length_df = execute_query(avg_length_query, (start_date, end_date))
    daily_messages_df = execute_query(daily_messages_query, (start_date, end_date))
    
    return {
        'total_users': users_df.iloc[0]['total_users'] if not users_df.empty else 0,
        'avg_conversation_length': round(avg_length_df.iloc[0]['avg_conversation_length'], 1) if not avg_length_df.empty else 0,
        'daily_messages': daily_messages_df
    }

def get_completion_candidates(start_date, end_date):
    """
    Récupérer les conversations candidates pour l'analyse de completion
    (derniers messages de chaque conversation)
    """
    query = """
    WITH last_messages AS (
        SELECT chatid, content, role, created_at,
               ROW_NUMBER() OVER (PARTITION BY chatid ORDER BY created_at DESC) as rn
        FROM public.messages 
        WHERE created_at >= %s AND created_at <= %s
    )
    SELECT chatid, content, role, created_at
    FROM last_messages 
    WHERE rn = 1
    ORDER BY created_at DESC
    """
    return execute_query(query, (start_date, end_date))

def get_conversations_summary_data(start_date, end_date):
    """
    Récupérer les données pour le tableau de résumé des conversations
    """
    query = """
    SELECT chatid,
           MIN(created_at) as start_time,
           MAX(created_at) as end_time,
           COUNT(*) as message_count,
           COUNT(CASE WHEN role = 'customer' THEN 1 END) as customer_messages,
           COUNT(CASE WHEN role = 'agent' THEN 1 END) as agent_messages
    FROM public.messages 
    WHERE created_at >= %s AND created_at <= %s
    GROUP BY chatid
    ORDER BY start_time DESC
    """
    return execute_query(query, (start_date, end_date))
