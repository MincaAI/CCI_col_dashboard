# 📊 Guide d'utilisation - Dashboard CCI France Colombia

## 🔗 Accès au dashboard

**URL :** https://cci-col-dashboard.streamlit.app/

**Identifiants de connexion :**
- **Nom d'utilisateur :** `cci-col`
- **Mot de passe :** `Maria2025!`

---

## 🚪 Connexion

1. Rendez-vous sur l'URL du dashboard
2. Saisissez le nom d'utilisateur : `cci-col`
3. Saisissez le mot de passe : `Maria2025!`
4. Cliquez sur **"Se connecter"**

---

## 🧭 Navigation principale

Le dashboard contient **2 sections principales** accessibles via la barre latérale gauche :

### 📈 **KPIs** (Indicateurs de performance)
- Vue d'ensemble des métriques clés
- Graphiques et statistiques

### 💬 **Conversations** 
- Tableau détaillé des conversations
- Lecteur de conversations individuel

---

## 📅 Sélection de période

Dans la **barre latérale gauche**, vous pouvez définir la période d'analyse :

- **Du :** Date de début (par défaut : 1er août 2025)
- **Au :** Date de fin (par défaut : aujourd'hui)

Les données se mettent à jour automatiquement selon la période sélectionnée.

---

## 📈 Section KPIs

### 🔢 Métriques principales (4 indicateurs)

1. **👥 Nombre total d'utilisateurs**
   - Nombre unique de conversations WhatsApp
   - Représente les contacts distincts

2. **💬 Longueur moyenne des conversations**
   - Nombre moyen de messages par conversation
   - Indicateur d'engagement

3. **✅ Taux de completion**
   - Pourcentage de conversations terminées avec un contact fourni
   - Mesure l'efficacité de MarIA

4. **📈 Nouvelles conversations**
   - Nombre total de nouvelles conversations sur la période
   - Indicateur d'activité

### 📊 Graphiques

**Graphique 1 : Nouvelles conversations par jour**
- Évolution quotidienne du nombre de nouvelles conversations
- Permet d'identifier les pics d'activité

**Graphique 2 : Analyse de completion**
- Répartition entre conversations complètes et incomplètes
- Graphique en secteurs (camembert)

---

## 💬 Section Conversations

### 📋 Tableau de résumé

Le tableau principal affiche pour chaque conversation :

- **Contact :** Numéro WhatsApp du client
- **Nom :** Nom du client (extrait par IA ou base de données)
- **Entreprise :** Nom de l'entreprise du client
- **Messages :** Nombre total de messages échangés
- **Dernière activité :** Date et heure du dernier message
- **Service d'intérêt :** Service CCI identifié par l'IA
- **Résumé :** Résumé automatique de la conversation

### 🔍 Fonctionnalités du tableau

- **Tri :** Cliquez sur les en-têtes de colonnes pour trier
- **Recherche :** Utilisez la barre de recherche pour filtrer
- **Pagination :** Naviguez entre les pages si nécessaire

### 📖 Lecteur de conversations

**Accès :** Onglet "🔍 Lecteur de conversations"

1. **Sélection de conversation :**
   - Menu déroulant avec toutes les conversations
   - Format : "Nom du client - Numéro - Date"

2. **Affichage des messages :**
   - **Messages client :** Fond rose avec bordure
   - **Messages MarIA :** Fond bleu avec bordure
   - Horodatage pour chaque message

3. **Informations détaillées :**
   - Durée de la conversation
   - Nombre total de messages
   - Statut de completion

---

## ⚙️ Fonctionnalités avancées

### 🤖 Analyses IA automatiques

Le système génère automatiquement :
- **Résumés de conversations** structurés
- **Extraction de noms** et entreprises
- **Identification des services** d'intérêt CCI
- **Analyse de completion** des conversations

### 📊 Génération de rapports

Pour générer les analyses manquantes, utilisez la commande suggérée dans l'interface :
```bash
python scripts/generate_analysis_batch.py --limit 2 --days 30
```

### 🔄 Actualisation des données

- Les données se mettent à jour automatiquement
- Changez la période pour voir différentes plages de données
- Les métriques se recalculent en temps réel

---

## 🎯 Cas d'usage typiques

### 📈 **Suivi de performance**
1. Allez dans **KPIs**
2. Consultez le taux de completion
3. Analysez l'évolution des nouvelles conversations

### 🔍 **Analyse d'une conversation spécifique**
1. Allez dans **Conversations**
2. Utilisez le **Lecteur de conversations**
3. Sélectionnez la conversation à analyser

### 📊 **Rapport mensuel**
1. Définissez la période (ex: 1er au 30 du mois)
2. Consultez les **KPIs** pour les métriques globales
3. Exportez ou notez les données du tableau

### 🎯 **Identification des besoins clients**
1. Consultez la colonne **"Service d'intérêt"** dans le tableau
2. Filtrez par type de service
3. Lisez les résumés pour comprendre les besoins

---

## ⚠️ Points d'attention

### 🔐 Sécurité
- **Ne partagez jamais** les identifiants de connexion
- Déconnectez-vous après utilisation (bouton en bas de la barre latérale)

### 📱 Données sensibles
- Les conversations contiennent des **données personnelles**
- Respectez la confidentialité des clients
- Utilisez les informations uniquement dans le cadre professionnel CCI

### 🔄 Performance
- Le chargement peut prendre quelques secondes pour les grandes périodes
- Les analyses IA sont générées en temps réel
- Patientez pendant les calculs (indicateurs de chargement affichés)

---

## 🆘 Support et dépannage

### ❓ Problèmes courants

**Connexion impossible :**
- Vérifiez l'URL : https://cci-col-dashboard.streamlit.app/
- Vérifiez les identifiants (sensibles à la casse)

**Données manquantes :**
- Vérifiez la période sélectionnée
- Certaines analyses peuvent prendre du temps à se générer

**Lenteur de chargement :**
- Normal pour les grandes périodes
- Réduisez la plage de dates si nécessaire

### 📞 Contact technique
Pour tout problème technique ou question sur l'utilisation, contactez l'équipe de développement.

---

## 🎉 Bonnes pratiques

1. **Consultez régulièrement** les KPIs pour suivre les performances
2. **Analysez les résumés** pour comprendre les besoins récurrents
3. **Utilisez les filtres** de période pour des analyses ciblées
4. **Respectez la confidentialité** des données clients
5. **Déconnectez-vous** après utilisation

---

*Dashboard développé avec ❤️ par **MincaAI** pour la CCI France Colombia*
