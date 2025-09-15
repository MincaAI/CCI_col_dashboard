# 🔐 CONFIGURATION SÉCURISÉE - CCI Dashboard

## ⚠️ IMPORTANT: Credentials compromis sur GitHub

Les anciens credentials ont été exposés sur GitHub. Suivez ces étapes pour sécuriser l'application.

## 1. Créer un nouveau fichier .env

Créez un fichier `.env` dans le dossier racine avec:

```bash
# Base de données
DATABASE_URL=postgresql://neondb_owner:npg_2yMelBFq0xcr@ep-round-sunset-adbyuw53-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# NOUVEAUX credentials sécurisés - CHANGEZ CES VALEURS!
AUTH_USERNAME=cci-colombia-admin
AUTH_PASSWORD=SecureCCI2025!#MarIA
```

## 2. Recommandations de mot de passe

Générez un mot de passe fort:
- Minimum 16 caractères
- Mélange majuscules/minuscules/chiffres/symboles
- Exemple: `CCI#Maria$2025!Dashboard`

## 3. Vérifications de sécurité

✅ Fichier .env dans .gitignore  
✅ Pas de credentials hardcodés dans le code  
✅ Validation des variables d'environnement  

## 4. Rotation des credentials

🔄 Changez régulièrement:
- Mot de passe dashboard
- Clé API OpenAI
- URL base de données si possible

## 5. Déploiement Streamlit Cloud

Pour Streamlit Cloud, ajoutez dans les secrets:
```toml
DATABASE_URL = "votre-url-db"
OPENAI_API_KEY = "votre-cle-openai"
AUTH_USERNAME = "nouveau-username"
AUTH_PASSWORD = "nouveau-password-fort"
```

⚠️ **JAMAIS** de credentials dans le code source!
