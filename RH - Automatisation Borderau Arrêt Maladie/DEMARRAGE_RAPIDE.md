# 🚀 Guide de Démarrage Rapide

## Déploiement en 5 minutes sur Streamlit Cloud

### Étape 1 : Préparer les fichiers
Vous avez besoin de ces 4 fichiers (déjà créés) :
- ✅ `app.py` - Application principale
- ✅ `pdf_extractor.py` - Module d'extraction
- ✅ `requirements.txt` - Dépendances
- ✅ `README.md` - Documentation

### Étape 2 : Créer un compte GitHub
1. Aller sur https://github.com
2. Cliquer sur "Sign up" (c'est gratuit)
3. Suivre les instructions

### Étape 3 : Créer un nouveau dépôt
1. Une fois connecté, cliquer sur le "+" en haut à droite
2. Sélectionner "New repository"
3. Nommer le dépôt : `extracteur-ijss`
4. Laisser "Public" sélectionné
5. Cliquer sur "Create repository"

### Étape 4 : Uploader les fichiers
Sur la page du dépôt nouvellement créé :
1. Cliquer sur "uploading an existing file"
2. Glisser-déposer les 4 fichiers mentionnés ci-dessus
3. Scroller en bas et cliquer sur "Commit changes"

### Étape 5 : Déployer sur Streamlit Cloud
1. Aller sur https://share.streamlit.io
2. Cliquer sur "Sign in" → Utiliser votre compte GitHub
3. Cliquer sur "New app"
4. Remplir le formulaire :
   - **Repository** : Sélectionner `votre-username/extracteur-ijss`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. Cliquer sur "Deploy!"

### Étape 6 : Attendre le déploiement
- Le déploiement prend environ 2-3 minutes
- Une URL sera générée (ex: `https://extracteur-ijss.streamlit.app`)
- Vous pouvez partager cette URL avec votre équipe RH

## 🎉 C'est terminé !

Votre application est maintenant en ligne et accessible depuis n'importe où !

## 📝 Utilisation de l'application

1. **Préparer les fichiers** : Mettre tous les PDFs de la Sécu dans un dossier
2. **Créer un ZIP** : Compresser le dossier en fichier ZIP
3. **Ouvrir l'app** : Aller sur l'URL Streamlit
4. **Upload** : Glisser-déposer le fichier ZIP
5. **Extraire** : Cliquer sur "Extraire les données"
6. **Télécharger** : Cliquer sur "Télécharger le fichier Excel"

## ⚙️ Configuration optionnelle

### Ajouter un mot de passe (optionnel)
Si vous voulez protéger l'application par mot de passe :

1. Créer un fichier `.streamlit/secrets.toml` dans votre dépôt GitHub
2. Ajouter :
```toml
password = "votre_mot_de_passe"
```
3. Modifier `app.py` pour ajouter l'authentification

### Personnaliser le thème
Le fichier `.streamlit/config.toml` contient les couleurs de l'application.
Vous pouvez les modifier selon vos préférences.

## 🆘 Besoin d'aide ?

### Problème : L'application ne démarre pas
- Vérifier que tous les fichiers sont bien uploadés sur GitHub
- Vérifier les logs dans Streamlit Cloud (bouton "Manage app")

### Problème : Les PDFs ne sont pas extraits
- Vérifier que les PDFs sont dans le ZIP
- Vérifier qu'ils ne sont pas protégés par mot de passe
- S'assurer qu'ils respectent le format standard CPAM

### Problème : Données incorrectes
- Vérifier que les PDFs correspondent au format attendu
- Consulter les exemples fournis

## 📧 Contact
Pour toute question, contacter le service informatique.

---
**Version 1.0** - Novembre 2025
