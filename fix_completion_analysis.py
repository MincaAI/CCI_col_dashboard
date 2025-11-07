#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les analyses de completion incorrectes
Marque automatiquement comme INCOMPLETE toutes les conversations avec moins de 3 messages
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurer UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from database.connection import execute_query
from dotenv import load_dotenv

load_dotenv()

def fix_short_conversations_completion():
    """
    Corriger toutes les conversations avec < 3 messages marquées à tort comme complètes
    """
    
    print("\n" + "="*60)
    print("CORRECTION DES ANALYSES DE COMPLETION")
    print("="*60 + "\n")
    
    # 1. Trouver les conversations avec < 3 messages marquées comme complètes
    check_query = """
    SELECT 
        ca.chatid,
        ca.is_completed,
        COUNT(m.messageid) as message_count
    FROM conversation_analysis ca
    LEFT JOIN message m ON ca.chatid::text = m.chatid::text
    WHERE ca.is_completed = true
    GROUP BY ca.chatid, ca.is_completed
    HAVING COUNT(m.messageid) < 3
    """
    
    print(">> Recherche des conversations incorrectement marquees comme completes...")
    incorrect_conversations = execute_query(check_query)
    
    if incorrect_conversations.empty:
        print("✓ Aucune correction necessaire. Toutes les analyses sont correctes.")
        return
    
    count = len(incorrect_conversations)
    print(f"\n! Trouve {count} conversation(s) avec < 3 messages marquees comme completes\n")
    
    # Afficher les détails (limiter à 10 exemples)
    for idx, row in incorrect_conversations.head(10).iterrows():
        chatid_str = str(row['chatid'])
        print(f"  - Chat ID: {chatid_str[:20]}... ({row['message_count']} messages)")
    
    # 2. Corriger ces conversations
    print(f"\n>> Correction en cours...")
    
    update_query = """
    UPDATE conversation_analysis ca
    SET is_completed = false,
        analysis_date = NOW()
    FROM (
        SELECT ca2.chatid
        FROM conversation_analysis ca2
        LEFT JOIN message m ON ca2.chatid::text = m.chatid::text
        WHERE ca2.is_completed = true
        GROUP BY ca2.chatid
        HAVING COUNT(m.messageid) < 3
    ) as short_convs
    WHERE ca.chatid = short_convs.chatid
    """
    
    try:
        execute_query(update_query, fetch=False)
        print(f"\n✓ {count} conversation(s) corrigee(s) avec succes!")
        print(f"  Ces conversations sont maintenant marquees comme INCOMPLETE")
    except Exception as e:
        print(f"\n✗ Erreur lors de la correction: {e}")
        return
    
    # 3. Afficher les statistiques finales
    print("\n" + "-"*60)
    print("STATISTIQUES FINALES")
    print("-"*60 + "\n")
    
    stats_query = """
    SELECT 
        COUNT(CASE WHEN ca.is_completed = true THEN 1 END) as completes,
        COUNT(CASE WHEN ca.is_completed = false THEN 1 END) as incompletes,
        COUNT(*) as total
    FROM conversation_analysis ca
    """
    
    stats = execute_query(stats_query)
    if not stats.empty:
        row = stats.iloc[0]
        total = row['total']
        completes = row['completes']
        incompletes = row['incompletes']
        
        if total > 0:
            pct_complete = (completes / total) * 100
            pct_incomplete = (incompletes / total) * 100
        else:
            pct_complete = 0
            pct_incomplete = 0
        
        print(f"Total conversations analysees: {total}")
        print(f"  - Completes: {completes} ({pct_complete:.1f}%)")
        print(f"  - Incompletes: {incompletes} ({pct_incomplete:.1f}%)")
    
    print("\n" + "="*60)
    print("CORRECTION TERMINEE")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        fix_short_conversations_completion()
    except KeyboardInterrupt:
        print("\n\n✗ Interruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erreur fatale: {e}")
        sys.exit(1)

