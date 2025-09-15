#!/usr/bin/env python3
"""
Script simple pour re-générer les résumés des 12 dernières conversations
avec le nouveau prompt mis à jour
"""

import subprocess
import sys
import os

def main():
    """
    Exécuter le script batch avec les bonnes options pour re-générer 
    les résumés des 12 dernières conversations
    """
    print("🔄 Re-génération des résumés des 12 dernières conversations")
    print("📋 Avec le nouveau prompt mis à jour")
    print("-" * 50)
    
    # Commande pour exécuter le script batch
    cmd = [
        sys.executable,  # Python executable
        "scripts/generate_analysis_batch.py",
        "--limit", "12",     # Limiter à 12 conversations
        "--days", "30",      # Chercher dans les 30 derniers jours
        "--force"            # Forcer la re-génération même si déjà analysé
    ]
    
    print(f"🚀 Exécution: {' '.join(cmd)}")
    print()
    
    try:
        # Exécuter le script
        result = subprocess.run(cmd, cwd=os.getcwd(), check=True)
        print("\n✅ Re-génération terminée avec succès!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
