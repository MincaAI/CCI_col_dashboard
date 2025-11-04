#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script autonome pour générer les analyses de conversations par batch
Exécute l'extraction de résumés, entreprises et prénoms via IA
Stocke les résultats directement en base PostgreSQL

Usage:
    python generate_analysis_batch.py [--limit N] [--days N] [--force]
    
Options:
    --limit N    : Traiter maximum N conversations (défaut: 50)
    --days N     : Analyser les conversations des N derniers jours (défaut: 7)
    --force      : Forcer l'analyse même si déjà fait
    --dry-run    : Simulation sans écriture en base
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI
import pandas as pd

# Forcer l'encodage UTF-8 au niveau du script
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Monkey patch pour forcer UTF-8 dans httpx
import httpx._models
original_normalize = httpx._models._normalize_header_value

def patched_normalize_header_value(value, encoding=None):
    """Force UTF-8 encoding for all headers"""
    if isinstance(value, str):
        # Force UTF-8, remove any non-ASCII characters
        value = value.encode('ascii', errors='ignore').decode('ascii')
    return original_normalize(value, encoding)

httpx._models._normalize_header_value = patched_normalize_header_value

# Ajouter le répertoire parent au PATH pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

from config.settings import DATABASE_URL, OPENAI_API_KEY
from utils.llm_analysis import generate_conversation_summary

class ConversationAnalyzer:
    """Classe principale pour analyser les conversations"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.connection = None
        # Créer le client OpenAI avec headers ASCII purs
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            default_headers={
                "User-Agent": "CCI-Colombia-Dashboard/1.0"
            }
        )
        self.stats = {
            'processed': 0,
            'summaries_generated': 0,
            'companies_extracted': 0,
            'names_extracted': 0,
            'errors': 0
        }
    
    def connect_db(self):
        """Connexion a la base de donnees"""
        try:
            self.connection = psycopg2.connect(
                DATABASE_URL,
                client_encoding='UTF8'
            )
            print(">> Connexion a PostgreSQL reussie")
            return True
        except Exception as e:
            print(f">> Erreur connexion DB: {e}")
            return False
    
    def get_conversations_to_analyze(self, days_back=7, limit=50, force=False):
        """Récupérer les conversations à analyser"""
        start_date = datetime.now() - timedelta(days=days_back)
        
        if force:
            # Analyser toutes les conversations, même déjà analysées (pour re-générer avec le nouveau prompt)
            query = """
            SELECT DISTINCT m.chatid::text as chatid,
                   MIN(m.created_at) as start_time,
                   MAX(m.created_at) as end_time,
                   COUNT(*) as message_count
            FROM public.message m
            WHERE m.created_at >= %s
            GROUP BY m.chatid
            ORDER BY MAX(m.created_at) DESC
            LIMIT %s
            """
            params = (start_date, limit)
        else:
            # Analyser seulement les nouvelles conversations ou celles sans analyse complète
            query = """
            SELECT DISTINCT m.chatid::text as chatid,
                   MIN(m.created_at) as start_time,
                   MAX(m.created_at) as end_time,
                   COUNT(*) as message_count
            FROM public.message m
            LEFT JOIN conversation_analysis ca ON m.chatid = ca.chatid
            WHERE m.created_at >= %s 
              AND (ca.chatid IS NULL OR ca.conversation_summary IS NULL OR ca.service_interest IS NULL)
            GROUP BY m.chatid
            ORDER BY MAX(m.created_at) DESC
            LIMIT %s
            """
            params = (start_date, limit)
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_conversation_messages(self, chatid):
        """Récupérer les messages d'une conversation"""
        query = """
        SELECT content, role, created_at
        FROM public.message 
        WHERE chatid::text = %s
        ORDER BY created_at ASC
        """
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (chatid,))
            return cursor.fetchall()
    
    def extract_client_name(self, messages):
        """Extraire le prénom/nom du client via IA"""
        try:
            print("    [DEBUG] Début extraction nom...")
            conversation_text = ""
            # Limiter aux 10 premiers messages pour économiser des tokens
            limited_messages = messages[:10]
            for msg in limited_messages:
                role = "Client" if msg['role'] == 'customer' else "MarIA"
                # Assurer l'encodage UTF-8 et nettoyer les caractères problématiques
                content = str(msg['content']) if msg['content'] else ""
                # Forcer l'encodage UTF-8
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                else:
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')
                # Limiter chaque message à 200 caractères
                content = content[:200]
                conversation_text += f"{role}: {content}\n"
            
            print(f"    [DEBUG] Texte conversation prepare: {len(conversation_text)} caracteres")
            
            # Creer le prompt en ASCII pur pour eviter les problemes
            prompt = """
            Analyse cette conversation entre MarIA (agent CCI) et un client pour identifier le NOM/PRENOM du client.
            
            CONVERSATION:
            """ + conversation_text + """
            
            Trouve le nom/prenom du client mentionne dans la conversation.
            
            Regles:
            - Cherche quand le client se presente ou donne son nom
            - Cherche quand MarIA utilise le nom du client
            - Si tu trouves un nom, reponds SEULEMENT le prenom (ou prenom + nom)
            - Si pas de nom trouve, reponds exactement "NON_TROUVE"
            
            Reponse (juste le nom):
            """
            
            print("    [DEBUG] Prompt cree, appel API OpenAI...")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,  # Réduit pour économiser
                temperature=0
            )
            
            print("    [DEBUG] Reponse API recue")
            result = response.choices[0].message.content.strip()
            return result if result != "NON_TROUVE" else None
            
        except Exception as e:
            import traceback
            print(f"    [DEBUG] ERREUR COMPLETE:")
            traceback.print_exc()
            print(f"Erreur extraction nom: {e}")
            return None
    
    def extract_company_name(self, messages):
        """Extraire le nom de l'entreprise via IA"""
        try:
            conversation_text = ""
            # Limiter aux 10 premiers messages pour économiser des tokens
            limited_messages = messages[:10]
            for msg in limited_messages:
                role = "Client" if msg['role'] == 'customer' else "MarIA"
                # Assurer l'encodage UTF-8 et nettoyer les caractères problématiques
                content = str(msg['content']) if msg['content'] else ""
                # Forcer l'encodage UTF-8
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                else:
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')
                # Limiter chaque message à 200 caractères
                content = content[:200]
                conversation_text += f"{role}: {content}\n"
            
            prompt = f"""
            Analyse cette conversation entre MarIA (agent CCI) et un client pour identifier le NOM DE L'ENTREPRISE du client.
            
            CONVERSATION:
            {conversation_text}
            
            Trouve le nom de l'entreprise/société du client mentionné dans la conversation.
            
            Règles:
            - Cherche quand le client mentionne son entreprise, société, compagnie
            - Cherche les noms d'entreprises dans le contexte professionnel
            - Si tu trouves un nom d'entreprise, réponds SEULEMENT le nom (sans "Entreprise:", "Société:", etc.)
            - Si pas d'entreprise trouvée, réponds exactement "NON_TROUVE"
            
            Réponse (juste le nom de l'entreprise):
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,  # Réduit de 50 à 30
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            return result if result != "NON_TROUVE" else None
            
        except Exception as e:
            print(f">> Erreur extraction entreprise: {e}")
            return None
    
    
    def analyze_service_interest(self, messages):
        """Analyser les services CCI qui intéressent le client"""
        try:
            # Préparer le texte de conversation (limité pour économiser)
            conversation_text = ""
            # Limiter aux 15 premiers messages
            limited_messages = messages[:15]
            for msg in limited_messages:
                role = "Client" if msg['role'] == 'customer' else "Agent"
                # Assurer l'encodage UTF-8 et nettoyer les caractères problématiques
                content = str(msg['content']) if msg['content'] else ""
                # Forcer l'encodage UTF-8
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                else:
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')
                # Limiter chaque message à 300 caractères
                content = content[:300]
                conversation_text += f"{role}: {content}\n\n"
            
            # Prompt raccourci pour économiser des tokens
            prompt = f"""Conversation CCI:
{conversation_text}

Services: 1-Commercial 2-Missions 3-Networking 4-Formation 5-Juridique 6-Etudes 7-Implantation 8-Communication 9-Admin 10-Info generale

Identifie le service principal (nom seulement):
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],  # Pas de system message pour économiser
                max_tokens=30,
                temperature=0
            )
            
            service_interest = response.choices[0].message.content.strip()
            return service_interest if service_interest else "Information générale"
            
        except Exception as e:
            print(f">> Erreur analyse service: {e}")
            return "Information générale"

    def analyze_completion(self, messages):
        """Analyser si la conversation est complète"""
        if not messages:
            return False, "Aucun message"
            
        # Assurer l'encodage UTF-8 et nettoyer les caractères problématiques
        last_message = str(messages[-1]['content']) if messages[-1]['content'] else ""
        # Forcer l'encodage UTF-8
        if isinstance(last_message, bytes):
            last_message = last_message.decode('utf-8', errors='ignore')
        else:
            last_message = last_message.encode('utf-8', errors='ignore').decode('utf-8')
        
        try:
            prompt = f"""
            Analyse ce message final d'une conversation avec l'agent MarIA de la CCI France Colombia.
            
            Message: "{last_message}"
            
            Détermine si cette conversation est COMPLÈTE selon ces critères:
            1. Le message contient un numéro de téléphone WhatsApp (format +57 xxx xxx xxxx)
            2. Le message indique une redirection vers un contact spécifique de l'équipe CCI
            
            Réponds uniquement par "COMPLETE" ou "INCOMPLETE".
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            is_complete = "COMPLETE" in result.upper()
            return is_complete, result
            
        except Exception as e:
            print(f">> Erreur analyse completion: {e}")
            return False, f"Erreur: {e}"
    
    def save_analysis_to_db(self, chatid, analysis_data):
        """Sauvegarder l'analyse en base de données"""
        if self.dry_run:
            print(f"[DRY-RUN] Sauvegarde pour {chatid}: {analysis_data}")
            return True
        
        try:
            query = """
            INSERT INTO conversation_analysis 
            (chatid, client_name, company_name, conversation_summary, 
             service_interest, total_messages, conversation_start_date, conversation_end_date, 
             is_completed, completion_analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chatid) 
            DO UPDATE SET
                client_name = EXCLUDED.client_name,
                company_name = EXCLUDED.company_name,
                conversation_summary = EXCLUDED.conversation_summary,
                service_interest = EXCLUDED.service_interest,
                total_messages = EXCLUDED.total_messages,
                conversation_start_date = EXCLUDED.conversation_start_date,
                conversation_end_date = EXCLUDED.conversation_end_date,
                is_completed = EXCLUDED.is_completed,
                completion_analysis = EXCLUDED.completion_analysis,
                last_updated = CURRENT_TIMESTAMP
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, (
                    chatid,
                    analysis_data['client_name'],
                    analysis_data['company_name'], 
                    analysis_data['summary'],
                    analysis_data['service_interest'],
                    analysis_data['total_messages'],
                    analysis_data['start_date'],
                    analysis_data['end_date'],
                    analysis_data['is_completed'],
                    analysis_data['completion_analysis']
                ))
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f">> Erreur sauvegarde DB: {e}")
            self.connection.rollback()
            return False
    
    def analyze_conversation(self, conversation):
        """Analyser une conversation complete"""
        chatid = conversation['chatid']
        print(f"\n>> Analyse conversation {chatid}...")
        
        # Recuperer les messages
        messages = self.get_conversation_messages(chatid)
        if not messages:
            print(f">> Aucun message trouve pour {chatid}")
            return False
        
        # Extractions IA
        print("  [1/5] Extraction du nom client...")
        client_name = self.extract_client_name(messages)
        if client_name:
            self.stats['names_extracted'] += 1
            print(f"  >> Nom trouve: {client_name}")
        else:
            print("  >> Nom non trouve")
        
        print("  [2/5] Extraction entreprise...")
        company_name = self.extract_company_name(messages)
        if company_name:
            self.stats['companies_extracted'] += 1
            print(f"  >> Entreprise trouvee: {company_name}")
        else:
            print("  >> Entreprise non trouvee")
        
        print("  [3/5] Generation resume...")
        # Convertir les messages au format DataFrame pour la fonction importee
        messages_df = pd.DataFrame(messages)
        summary = generate_conversation_summary(messages_df)
        if summary and summary != "Resume non disponible":
            self.stats['summaries_generated'] += 1
            print(f"  >> Resume genere ({len(summary)} caracteres)")
        else:
            print("  >> Erreur generation resume")
        
        print("  [4/5] Analyse service d'interet...")
        service_interest = self.analyze_service_interest(messages)
        if service_interest:
            print(f"  >> Service identifie: {service_interest}")
        else:
            print("  >> Service non identifie")
        
        print("  [5/5] Analyse completion...")
        is_completed, completion_analysis = self.analyze_completion(messages)
        
        # Préparer les données pour sauvegarde
        analysis_data = {
            'client_name': client_name,
            'company_name': company_name,
            'summary': summary,
            'service_interest': service_interest,
            'total_messages': conversation['message_count'],
            'start_date': conversation['start_time'],
            'end_date': conversation['end_time'],
            'is_completed': is_completed,
            'completion_analysis': completion_analysis
        }
        
        # Sauvegarder en base
        if self.save_analysis_to_db(chatid, analysis_data):
            print(f"  >> Sauvegarde reussie")
            self.stats['processed'] += 1
            return True
        else:
            print(f"  >> Erreur sauvegarde")
            self.stats['errors'] += 1
            return False
    
    def run_batch_analysis(self, days_back=7, limit=50, force=False):
        """Executer l'analyse en batch"""
        print(f">> Demarrage analyse batch...")
        print(f">> Periode: {days_back} derniers jours")
        print(f">> Limite: {limit} conversations")
        print(f">> Force: {'Oui' if force else 'Non'}")
        print(f">> Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        
        if not self.connect_db():
            return False
        
        # Recuperer les conversations a analyser
        conversations = self.get_conversations_to_analyze(days_back, limit, force)
        print(f"\n>> {len(conversations)} conversation(s) a analyser")
        
        if not conversations:
            print(">> Aucune nouvelle conversation a analyser")
            return True
        
        # Analyser chaque conversation
        start_time = time.time()
        
        for i, conversation in enumerate(conversations, 1):
            print(f"\n[{i}/{len(conversations)}]", end="")
            try:
                self.analyze_conversation(conversation)
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
            except Exception as e:
                print(f">> Erreur inattendue: {e}")
                self.stats['errors'] += 1
        
        # Statistiques finales
        elapsed = time.time() - start_time
        print(f"\n" + "="*50)
        print(f">> STATISTIQUES FINALES")
        print(f"="*50)
        print(f">> Temps total: {elapsed:.1f}s")
        print(f">> Conversations traitees: {self.stats['processed']}")
        print(f">> Resumes generes: {self.stats['summaries_generated']}")
        print(f">> Entreprises extraites: {self.stats['companies_extracted']}")
        print(f">> Noms extraits: {self.stats['names_extracted']}")
        print(f">> Erreurs: {self.stats['errors']}")
        
        if self.connection:
            self.connection.close()
            
        return self.stats['errors'] == 0

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Generation d\'analyses de conversations par batch')
    parser.add_argument('--limit', type=int, default=50, help='Nombre max de conversations a traiter')
    parser.add_argument('--days', type=int, default=7, help='Analyser les N derniers jours')
    parser.add_argument('--force', action='store_true', help='Forcer l\'analyse et re-generer tous les resumes meme si deja fait')
    parser.add_argument('--dry-run', action='store_true', help='Simulation sans ecriture en base')
    
    args = parser.parse_args()
    
    print(f">> Script d'analyse automatique de conversations CCI Colombia")
    print(f">> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyzer = ConversationAnalyzer(dry_run=args.dry_run)
    success = analyzer.run_batch_analysis(
        days_back=args.days,
        limit=args.limit,
        force=args.force
    )
    
    if success:
        print(f"\n>> Analyse terminee avec succes!")
        exit(0)
    else:
        print(f"\n>> Analyse terminee avec des erreurs!")
        exit(1)

if __name__ == "__main__":
    main()
