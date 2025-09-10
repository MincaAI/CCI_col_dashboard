"""
Configuration settings for CCI Colombia Dashboard
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration d'authentification
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "cci-col")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "Maria2025!")

# Configuration de l'application
APP_TITLE = "Dashboard CCI France Colombia"
APP_SUBTITLE = "Tableau de bord de l'agent MarIA"

# Services CCI et contacts
CCI_SERVICES = {
    "Diagnostic de marché": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Recherche de partenaires commerciaux": {"responsable": "Yasmine Azlabi", "whatsapp": "+57 304 658 9045"},
    "Mission commerciale": {"responsable": "Yasmine Azlabi", "whatsapp": "+57 304 658 9045"},
    "Veille de marché": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Participation aux foires": {"responsable": "Yasmine Azlabi", "whatsapp": "+57 304 658 9045"},
    "Gestion salariale": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Gestion de visa": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Assistance commerciale": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Domiciliation virtuelle": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Location de bureaux": {"responsable": "Nicolás Velásquez", "whatsapp": "+57 310 850 9941"},
    "Accès base de données": {"responsable": "Valentina Copete", "whatsapp": "+57 304 423 6731"},
    "Commercial à temps partagé": {"responsable": "Yasmine Azlabi", "whatsapp": "+57 304 658 9045"},
    "Agenda rendez-vous B2B": {"responsable": "Yasmine Azlabi", "whatsapp": "+57 304 658 9045"},
    "Comités thématiques": {"responsable": "Valentina Copete", "whatsapp": "+57 304 423 6731"},
    "Formations": {"responsable": "Valentina Copete", "whatsapp": "+57 304 423 6731"},
    "Pépinière d'entreprises": {"responsable": "Valentina Copete", "whatsapp": "+57 304 423 6731"},
    "Relations publiques": {"responsable": "Anouk Esnault", "whatsapp": "+57 301 806 2811"},
    "Communication": {"responsable": "Anouk Esnault", "whatsapp": "+57 301 806 2811"},
    "Événements": {"responsable": "Valentina Copete / Laura Morales", "whatsapp": "Variable selon ville"}
}

# Les 6 thèmes de MarIA
MARIA_THEMES = [
    "Utilisation actuelle des services",
    "Expérience avec les services", 
    "Objectif principal en Colombie",
    "Attentes d'accompagnement",
    "Perception de valeur de la CCI",
    "Suggestions d'amélioration"
]

# Configuration des couleurs CCI
CCI_COLORS = {
    "primary": "#1B4F72",
    "secondary": "#E91E63", 
    "background": "#FFFFFF",
    "text": "#1B4F72"
}
