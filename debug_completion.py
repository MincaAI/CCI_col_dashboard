"""
Script de debug pour analyser les conversations courtes marquées comme complètes
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from database.connection import execute_query
from utils.llm_analysis import analyze_conversation_completion

def debug_short_complete_conversations(start_date=None, end_date=None):
    """
    Analyser les conversations courtes (≤ 3 messages) marquées comme complètes
    """
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    print(f"🔍 Analyse des conversations courtes du {start_date} au {end_date}")
    print("=" * 80)
    
    # Récupérer toutes les conversations avec leur nombre de messages
    query = """
    WITH conversation_stats AS (
        SELECT 
            chatid::text as chatid,
            COUNT(*) as message_count,
            ARRAY_AGG(content ORDER BY created_at) as all_messages,
            ARRAY_AGG(role ORDER BY created_at) as all_roles,
            (ARRAY_AGG(content ORDER BY created_at DESC))[1] as last_message
        FROM public.message 
        WHERE created_at >= %s AND created_at <= %s
        GROUP BY chatid
    )
    SELECT * FROM conversation_stats
    WHERE message_count <= 3
    ORDER BY message_count ASC
    """
    
    short_conversations = execute_query(query, (start_date, end_date))
    
    if short_conversations.empty:
        print("❌ Aucune conversation courte trouvée dans cette période")
        return
    
    print(f"📊 {len(short_conversations)} conversations avec ≤ 3 messages trouvées")
    print()
    
    completed_count = 0
    
    for idx, conversation in short_conversations.iterrows():
        chatid = conversation['chatid']
        message_count = conversation['message_count']
        last_message = conversation['last_message']
        all_messages = conversation['all_messages']
        all_roles = conversation['all_roles']
        
        print(f"🗣️ Conversation {chatid} ({message_count} messages)")
        print("-" * 60)
        
        # Afficher tous les messages
        for i, (message, role) in enumerate(zip(all_messages, all_roles)):
            speaker = "🤖 MarIA" if role == 'agent' else "👤 Client"
            print(f"{i+1}. {speaker}: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        print(f"\n📝 Dernier message analysé: '{last_message[:150]}{'...' if len(last_message) > 150 else ''}'\n")
        
        # Analyser la completion
        try:
            is_complete = analyze_conversation_completion(last_message)
            status = "✅ COMPLÈTE" if is_complete else "❌ INCOMPLÈTE"
            print(f"🎯 Résultat: {status}")
            
            if is_complete:
                completed_count += 1
                print("⚠️  ATTENTION: Cette conversation courte est marquée comme complète!")
        except Exception as e:
            print(f"❌ Erreur d'analyse: {e}")
        
        print("=" * 80)
        print()
    
    completion_rate = (completed_count / len(short_conversations)) * 100
    print(f"📈 Résumé: {completed_count}/{len(short_conversations)} conversations courtes marquées comme complètes ({completion_rate:.1f}%)")
    
    if completed_count > 0:
        print("⚠️  Problème détecté: Des conversations courtes sont marquées comme complètes!")
        print("💡 Actions recommandées:")
        print("   1. Vérifier les critères de completion")
        print("   2. Améliorer le prompt d'analyse IA")
        print("   3. Ajouter une validation sur le nombre minimum de messages")

if __name__ == "__main__":
    debug_short_complete_conversations()


