"""
Module de connexion à la base de données PostgreSQL
"""
import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from config.settings import DATABASE_URL

@st.cache_resource
def get_database_connection():
    """
    Créer une connexion à la base de données PostgreSQL
    """
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        # Connexion échouée - retourner silencieusement None
        return None

def execute_query(query, params=None, fetch=True):
    """
    Exécuter une requête SQL et retourner les résultats
    """
    try:
        engine = get_database_connection()
        if engine is None:
            # Connexion échouée - retourner silencieusement des données vides
            return pd.DataFrame() if fetch else None
        
        if fetch:
            # Pour les requêtes SELECT - retour à la méthode simple qui fonctionnait
            df = pd.read_sql_query(query, engine, params=params)
            return df
        else:
            # Pour les requêtes UPDATE/INSERT
            with engine.connect() as connection:
                if params:
                    connection.execute(query, params)
                else:
                    connection.execute(query)
                connection.commit()
            return True
            
    except Exception as e:
        # Ne plus afficher les erreurs PostgreSQL à l'utilisateur
        # Juste logger en silence et retourner des données vides
        import logging
        logging.warning(f"Erreur DB silencieuse: {e}")
        return pd.DataFrame() if fetch else False

def test_connection():
    """
    Tester la connexion à la base de données
    """
    try:
        engine = get_database_connection()
        if engine is None:
            return False
        
        # Test simple avec pandas
        df = pd.read_sql_query("SELECT 1 as test", engine)
        return len(df) > 0
    except Exception as e:
        # Test échoué - retourner silencieusement False
        return False
