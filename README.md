# 🇨🇴 Dashboard CCI France Colombia - Agent MarIA

Dashboard interactif pour analyser les performances de l'agent conversationnel MarIA de la Chambre de Commerce et d'Industrie France Colombia.

## 🎯 Fonctionnalités

### 📊 Section KPIs
- **Nombre total d'utilisateurs** : Conversations WhatsApp uniques
- **Longueur moyenne des conversations** : Messages par conversation
- **Taux de completion** : Conversations terminées avec contact fourni (détection IA)
- **Messages par jour** : Évolution temporelle
- **Graphiques interactifs** : Visualisations avec Plotly

### 💬 Section Conversations
- **Tableau paginé** : Toutes les conversations avec détails
- **Résumés IA** : Synthèses automatiques avec OpenAI GPT-4
- **Analyse des thèmes** : Les 6 thèmes de MarIA couverts
- **Export CSV** : Données complètes exportables
- **Vue détaillée** : Messages complets par conversation

## 🚀 Installation et Déploiement

### Prérequis
- Python 3.8+
- PostgreSQL (base de données Neon)
- Clé API OpenAI
- Compte Streamlit Cloud (pour déploiement)

### Installation locale

1. **Cloner le repository**
```bash
git clone https://github.com/MincaAI/CCI_col_dashboard.git
cd CCI_col_dashboard
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos credentials
```

4. **Variables à configurer dans .env**
```bash
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
OPENAI_API_KEY=sk-your-openai-api-key-here
AUTH_USERNAME=cci-col
AUTH_PASSWORD=Maria2025!
```

5. **Lancer l'application**
```bash
streamlit run app.py
```

### Déploiement sur Streamlit Cloud

1. **Push sur GitHub** (déjà fait)
2. **Connecter à Streamlit Cloud** : https://share.streamlit.io/
3. **Configurer les secrets** dans Streamlit Cloud :
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `AUTH_USERNAME`
   - `AUTH_PASSWORD`

## 🏗️ Architecture du Projet

```
CCI_col_dashboard/
├── app.py                 # Application Streamlit principale
├── requirements.txt       # Dépendances Python
├── .env.example          # Template variables d'environnement
├── .streamlit/
│   └── config.toml       # Configuration Streamlit
├── config/
│   └── settings.py       # Configuration et constantes
├── database/
│   ├── connection.py     # Connexion PostgreSQL
│   └── queries.py        # Requêtes SQL
├── components/
│   ├── kpis.py          # Composants KPIs
│   └── conversations.py # Composants conversations
├── utils/
│   ├── auth.py          # Authentification
│   └── llm_analysis.py  # Analyses IA OpenAI
├── assets/              # Images et CSS
└── README.md
```

## 🤖 Agent MarIA - Contexte

MarIA est l'assistante virtuelle de la CCI France Colombia qui guide les membres à travers **6 thèmes principaux** :

1. **Utilisation actuelle des services**
2. **Expérience avec les services**
3. **Objectif principal en Colombie**
4. **Attentes d'accompagnement**
5. **Perception de valeur de la CCI**
6. **Suggestions d'amélioration**

### Services CCI analysés
- Diagnostic de marché
- Recherche de partenaires commerciaux
- Missions commerciales
- Veille de marché
- Participation aux foires
- Et 14 autres services...

## 🔐 Authentification

- **Utilisateur** : `cci-col`
- **Mot de passe** : `Maria2025!`
- Session sécurisée avec Streamlit

## 📊 Base de Données

### Schema PostgreSQL
```sql
Table: messages
- messageid (UUID)
- chatid (UUID) 
- content (TEXT)
- role (TEXT) - 'customer' ou 'agent'
- created_at (TIMESTAMP)
```

### Connexion
- **Provider** : Neon PostgreSQL
- **SSL** : Requis
- **Pooling** : Activé

## 🤖 Intégration IA

### OpenAI GPT-4
- **Résumés de conversations** : Analyse structurée automatique
- **Détection de completion** : Identification des conversations terminées
- **Analyse des thèmes** : Couverture des 6 thèmes MarIA

### Prompts optimisés
- Résumés en français
- Format structuré (Profil, Besoins, Services, Statut, Points clés)
- Analyse de completion via détection de numéros WhatsApp

## 📈 KPIs et Métriques

### Métriques principales
- **Utilisateurs uniques** : Basé sur chatid
- **Taux de completion** : Via analyse IA des derniers messages
- **Longueur conversations** : Moyenne des messages par chat
- **Évolution temporelle** : Messages par jour

### Visualisations
- **Graphiques en ligne** : Évolution des messages
- **Graphiques secteurs** : Répartition completion
- **Métriques temps réel** : Actualisation automatique

## 🎨 Design et UX

### Couleurs CCI
- **Primaire** : #1B4F72 (Bleu CCI)
- **Secondaire** : #E91E63 (Rose CCI)
- **Background** : #FFFFFF
- **Text** : #1B4F72

### Interface
- **Design responsif** : Adaptation mobile/desktop
- **Navigation intuitive** : Onglets KPIs/Conversations
- **Feedback utilisateur** : Messages de statut et spinners

## 🔧 Maintenance et Support

### Logs et Debug
- Erreurs de connexion DB affichées
- Status de connexion en sidebar
- Messages d'erreur utilisateur-friendly

### Performance
- **Cache Streamlit** : Connexions DB mises en cache
- **Pagination** : 20 conversations par page
- **Lazy loading** : Résumés IA générés à la demande

## 📞 Support

- **Développé par** : MincaAI
- **Client** : CCI France Colombia
- **Agent** : MarIA

Pour toute question technique, contacter l'équipe de développement MincaAI.

## 📄 Licence

Projet propriétaire CCI France Colombia - MincaAI

---

*Dashboard créé avec ❤️ pour optimiser l'expérience client de l'agent MarIA*