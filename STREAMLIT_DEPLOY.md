# 🚀 Guide de Déploiement - Streamlit Cloud

## ✅ Corrections Appliquées

Les problèmes suivants ont été résolus :

1. ✅ **Session cache problématique** - Suppression du cache qui causait des sessions corrompues
2. ✅ **Support des secrets Streamlit** - Le code lit maintenant à la fois `.env` (local) et `st.secrets` (Cloud)
3. ✅ **Problème de chargement infini** - La session est maintenant correctement gérée

---

## 📋 Étapes de Déploiement sur Streamlit Cloud

### 1. Préparer votre Compte Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez-vous avec votre compte GitHub
3. Autorisez l'accès à votre repository

### 2. Déployer l'Application

1. Cliquez sur **"New app"**
2. Sélectionnez :
   - **Repository** : Votre repo GitHub
   - **Branch** : `main`
   - **Main file path** : `app.py`
3. Cliquez sur **"Advanced settings"** (avant de déployer)

### 3. ⚠️ IMPORTANT : Configurer les Secrets

Dans **Advanced settings** → **Secrets**, ajoutez :

```toml
# Base de données PostgreSQL
DATABASE_URL = "postgresql://neondb_owner:npg_2yMelBFq0xcr@ep-round-sunset-adbyuw53-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# OpenAI API Key
OPENAI_API_KEY = "sk-votre-cle-openai-ici"

# Authentification Dashboard
AUTH_USERNAME = "cci-col"
AUTH_PASSWORD = "Maria2025!"
```

**⚠️ CHANGEZ LA CLÉ OPENAI !**

### 4. Déployer

Cliquez sur **"Deploy!"** - L'application sera en ligne en 2-3 minutes.

---

## 🔧 Tests en Local

Pour tester localement **avant** de déployer :

```bash
# 1. Créer/Mettre à jour le fichier .env
cp .env.example .env  # ou créez .env manuellement
nano .env  # Ajoutez vos credentials

# 2. Lancer Streamlit
streamlit run app.py
```

Le fichier `.streamlit/secrets.toml` a été créé automatiquement avec les mêmes valeurs que `.env` pour compatibilité.

---

## 🆘 Dépannage

### Problème : "Session expirée" ou page bloquée

**Solution** : Videz le cache de votre navigateur ou ouvrez en mode incognito

```bash
# Sur Mac : Cmd + Shift + Delete
# Sur Windows : Ctrl + Shift + Delete
```

### Problème : "Configuration manquante"

**Cause** : Les secrets ne sont pas configurés correctement

**Solution** : 
1. Allez dans les settings de votre app Streamlit Cloud
2. Section "Secrets"
3. Vérifiez que TOUS les secrets sont présents (voir section 3 ci-dessus)

### Problème : "Erreur de connexion à la base de données"

**Cause** : L'URL de la base de données est incorrecte ou la base de données est inaccessible

**Solution** :
1. Vérifiez que l'URL dans les secrets est exacte
2. Vérifiez que la base de données Neon est accessible (pas suspendue)

---

## 🔐 Sécurité

### ⚠️ NE JAMAIS commiter :

- ❌ `.env`
- ❌ `.streamlit/secrets.toml`
- ❌ Clés API dans le code

### ✅ Déjà protégé par `.gitignore` :

```
.env
.streamlit/secrets.toml
```

### 🔄 Rotation des Credentials

Pour changer les credentials :

1. **Sur Streamlit Cloud** : Settings → Secrets → Modifier
2. **En local** : Modifiez `.env`
3. Redémarrez l'application

---

## 📊 URLs de l'Application

- **Production** : https://votre-app.streamlit.app
- **Local** : http://localhost:8501

---

## 🆘 Support

En cas de problème :

1. Vérifiez les logs Streamlit Cloud (dans l'interface)
2. Vérifiez que tous les secrets sont configurés
3. Testez en local d'abord avec `streamlit run app.py`

**Credentials par défaut** :
- Username : `cci-col`
- Password : `Maria2025!`


