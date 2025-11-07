"""
Exécution de la suppression des conversations spécifiques
ATTENTION: Ce script supprime définitivement des données !
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

from database.connection import execute_query

# Liste des chatids à supprimer
CHATIDS_TO_DELETE = [
    "45f4d02f-051a-4ca9-ae9c-a029fe092e8e",
    "694635f7-6019-47a6-b79a-1e4d51bdb991", 
    "72b13539-e218-49a7-9ab0-05bfeea0a3d0",
    "7aae4dfb-3c43-40dc-ba55-f6755bfb225f",
    "88927542-b7e3-459a-a6a5-3954c3a132f7",
    "96ab4598-5cec-4df9-b40a-54e02bbfd5ab",
    "d3cff4f0-939f-4560-967c-f76f97bb6689",
    "ef70e812-7245-407a-88af-be1e036660e1",
    "f1d851f2-1268-4c3e-a58b-93a40498888f",
    "f5d1e7d0-b380-44e0-a26d-102ba2ae265b"
]

def create_backup_all():
    """
    Créer une sauvegarde de toutes les conversations à supprimer
    """
    print("💾 CRÉATION DE LA SAUVEGARDE GLOBALE...")
    
    # Créer une requête pour toutes les conversations
    placeholders = ','.join(['%s'] * len(CHATIDS_TO_DELETE))
    query = f"""
    SELECT messageid::text as messageid,
           chatid::text as chatid,
           content,
           role,
           created_at
    FROM public.message 
    WHERE chatid::text IN ({placeholders})
    ORDER BY chatid, created_at ASC
    """
    
    try:
        result = execute_query(query, tuple(CHATIDS_TO_DELETE))
        
        if not result.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_conversations_batch_{timestamp}.csv"
            result.to_csv(backup_filename, index=False)
            print(f"✅ Sauvegarde créée: {backup_filename}")
            print(f"📊 {len(result)} messages sauvegardés")
            return backup_filename
        else:
            print("⚠️ Aucun message trouvé pour les chatids spécifiés")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

def delete_conversations_batch():
    """
    Supprimer toutes les conversations en lot
    """
    print("🗑️ SUPPRESSION EN LOT...")
    
    # Créer une requête de suppression pour tous les chatids
    placeholders = ','.join(['%s'] * len(CHATIDS_TO_DELETE))
    delete_query = f"""
    DELETE FROM public.message 
    WHERE chatid::text IN ({placeholders})
    """
    
    try:
        # Compter les messages avant suppression
        count_query = f"""
        SELECT COUNT(*) as total_messages
        FROM public.message 
        WHERE chatid::text IN ({placeholders})
        """
        
        count_result = execute_query(count_query, tuple(CHATIDS_TO_DELETE))
        messages_before = count_result.iloc[0]['total_messages'] if not count_result.empty else 0
        
        print(f"📊 {messages_before} messages à supprimer")
        
        if messages_before == 0:
            print("⚠️ Aucun message trouvé à supprimer")
            return False
        
        # Exécuter la suppression
        execute_query(delete_query, CHATIDS_TO_DELETE)
        
        # Vérifier la suppression
        count_result_after = execute_query(count_query, CHATIDS_TO_DELETE)
        messages_after = count_result_after.iloc[0]['total_messages'] if not count_result_after.empty else 0
        
        messages_deleted = messages_before - messages_after
        
        print(f"✅ {messages_deleted} messages supprimés")
        
        if messages_after == 0:
            print("✅ Suppression complète confirmée")
            return True
        else:
            print(f"⚠️ {messages_after} messages restants")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        return False

def verify_final_state():
    """
    Vérifier l'état final après suppression
    """
    print("🔍 VÉRIFICATION DE L'ÉTAT FINAL...")
    
    # Compter le nombre total de conversations restantes
    total_query = "SELECT COUNT(DISTINCT chatid) as total FROM public.message"
    total_result = execute_query(total_query)
    new_total = total_result.iloc[0]['total'] if not total_result.empty else 0
    
    print(f"📊 Conversations restantes dans la base: {new_total}")
    
    # Lister les conversations restantes
    remaining_query = """
    SELECT DISTINCT chatid::text as chatid, 
           MIN(created_at) as first_message,
           COUNT(*) as message_count
    FROM public.message 
    GROUP BY chatid
    ORDER BY first_message DESC
    """
    
    remaining_result = execute_query(remaining_query)
    
    if not remaining_result.empty:
        print("📋 Conversations restantes:")
        for i, row in remaining_result.iterrows():
            print(f"   {i+1}. {row['chatid'][:12]}... ({row['message_count']} messages)")
    
    return new_total

def main():
    """
    Fonction principale - Exécution directe
    """
    print("🗑️ EXÉCUTION DE LA SUPPRESSION")
    print("⚠️  Suppression confirmée par l'utilisateur")
    print("=" * 60)
    
    # 1. Créer la sauvegarde
    backup_file = create_backup_all()
    
    if not backup_file:
        print("❌ Impossible de créer la sauvegarde. Suppression annulée.")
        return False
    
    print("\n" + "=" * 60)
    
    # 2. Supprimer les conversations
    success = delete_conversations_batch()
    
    print("\n" + "=" * 60)
    
    # 3. Vérifier l'état final
    final_count = verify_final_state()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ SUPPRESSION TERMINÉE AVEC SUCCÈS")
        print(f"💾 Sauvegarde disponible: {backup_file}")
        print(f"📊 Conversations supprimées: 10")
        print(f"📊 Conversations restantes: {final_count}")
        print(f"🎯 Le dashboard devrait maintenant afficher {final_count} conversations")
        return True
    else:
        print("❌ ERREUR LORS DE LA SUPPRESSION")
        return False

if __name__ == "__main__":
    main()
