#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script direct pour corriger les analyses de completion incorrectes
"""

import sys
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def fix_completion():
    """Corriger directement les conversations avec < 3 messages"""
    
    print("\n" + "="*60)
    print("CORRECTION DES ANALYSES DE COMPLETION")
    print("="*60 + "\n")
    
    # Connexion directe à PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # 1. Compter les conversations à corriger
        cursor.execute("""
            SELECT COUNT(*)
            FROM conversation_analysis ca
            WHERE ca.is_completed = true
            AND (
                SELECT COUNT(*)
                FROM message m
                WHERE m.chatid::text = ca.chatid::text
            ) < 3
        """)
        
        count_before = cursor.fetchone()[0]
        print(f"Conversations a corriger: {count_before}\n")
        
        if count_before == 0:
            print("Aucune correction necessaire.")
            conn.close()
            return
        
        # 2. Faire la correction
        print(">> Mise a jour en cours...")
        cursor.execute("""
            UPDATE conversation_analysis ca
            SET is_completed = false,
                analysis_date = NOW()
            WHERE ca.is_completed = true
            AND (
                SELECT COUNT(*)
                FROM message m
                WHERE m.chatid::text = ca.chatid::text
            ) < 3
        """)
        
        conn.commit()
        print(f"✓ {count_before} conversations corrigees!\n")
        
        # 3. Statistiques finales
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_completed = true THEN 1 END) as completes,
                COUNT(CASE WHEN is_completed = false THEN 1 END) as incompletes
            FROM conversation_analysis
        """)
        
        result = cursor.fetchone()
        total, completes, incompletes = result
        
        if total > 0:
            pct_complete = (completes / total) * 100
            pct_incomplete = (incompletes / total) * 100
        else:
            pct_complete = 0
            pct_incomplete = 0
        
        print("-"*60)
        print("STATISTIQUES FINALES")
        print("-"*60)
        print(f"Total: {total} conversations")
        print(f"  - Completes: {completes} ({pct_complete:.1f}%)")
        print(f"  - Incompletes: {incompletes} ({pct_incomplete:.1f}%)")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_completion()

