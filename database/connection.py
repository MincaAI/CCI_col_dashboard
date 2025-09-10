"""
Module de connexion à la base de données PostgreSQL
"""
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
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
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

def execute_query(query, params=None):
    """
    Exécuter une requête SQL et retourner les résultats
    """
    try:
        engine = get_database_connection()
        if engine is None:
            return None
        
        df = pd.read_sql_query(query, engine, params=params)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return None

def test_connection():
    """
    Tester la connexion à la base de données
    """
    try:
        engine = get_database_connection()
        if engine is None:
            return False
        
        # Test simple de connexion
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return True
    except Exception as e:
        st.error(f"Test de connexion échoué: {e}")
        return False
