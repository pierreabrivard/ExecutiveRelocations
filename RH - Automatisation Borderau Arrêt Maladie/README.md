# Extracteur de Bordereaux IJSS

Application Streamlit pour extraire automatiquement les données des bordereaux d'Indemnités Journalières de la Sécurité Sociale.

## 📋 Fonctionnalités

- Upload d'un fichier ZIP contenant plusieurs bordereaux PDF
- Extraction automatique des informations clés :
  - Date de paiement
  - Nom du bénéficiaire
  - Nature de la prestation
  - Dates de début et fin
  - Quantité
  - Montants remboursés (brut et net)
- Export des données dans un fichier Excel
- Interface utilisateur simple et intuitive

## 🚀 Déploiement sur Streamlit Cloud

### Prérequis
- Compte GitHub (gratuit)
- Compte Streamlit Cloud (gratuit)

### Étapes de déploiement

1. **Créer un dépôt GitHub**
   - Aller sur https://github.com
   - Cliquer sur "New repository"
   - Nommer le dépôt (ex: "extracteur-ijss")
   - Le créer (public ou privé)

2. **Uploader les fichiers**
   - Uploader ces 4 fichiers dans votre dépôt GitHub :
     - `app.py`
     - `pdf_extractor.py`
     - `requirements.txt`
     - `README.md`

3. **Déployer sur Streamlit Cloud**
   - Aller sur https://share.streamlit.io
   - Se connecter avec votre compte GitHub
   - Cliquer sur "New app"
   - Sélectionner votre dépôt
   - Choisir la branche "main"
   - Spécifier le fichier principal : `app.py`
   - Cliquer sur "Deploy!"

4. **Attendre le déploiement**
   - Le déploiement prend 2-3 minutes
   - Vous recevrez une URL publique (ex: https://votre-app.streamlit.app)

## 💻 Installation locale (pour développement)

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/extracteur-ijss.git
cd extracteur-ijss

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

## 📖 Utilisation

1. Préparer vos bordereaux PDF dans un dossier
2. Créer un fichier ZIP contenant tous les PDF
3. Aller sur l'application web
4. Uploader le fichier ZIP
5. Cliquer sur "Extraire les données"
6. Télécharger le fichier Excel généré

## 🔧 Structure du projet

```
extracteur-ijss/
│
├── app.py                 # Application Streamlit principale
├── pdf_extractor.py       # Module d'extraction des données PDF
├── requirements.txt       # Dépendances Python
└── README.md             # Documentation
```

## 📝 Format des PDF supportés

L'application supporte les bordereaux IJSS au format standard de l'Assurance Maladie avec :
- En-tête contenant "Journée du JJ/MM/AAAA"
- Section "Détail des prestations pour [NOM BENEFICIAIRE]"
- Tableau avec dates, nature des prestations, quantités et montants
- Ligne "Total" avec le montant net

## 🛠️ Technologies utilisées

- **Streamlit** : Framework web pour l'interface
- **PyMuPDF (fitz)** : Extraction de texte des PDF
- **Pandas** : Manipulation des données
- **OpenPyXL** : Génération de fichiers Excel

## ⚠️ Remarques importantes

- Les fichiers sont traités temporairement et ne sont pas stockés
- Les données sont extraites localement, aucune donnée n'est envoyée à des serveurs externes
- Le format des PDF doit correspondre au format standard de l'Assurance Maladie

## 🐛 Résolution de problèmes

**Problème : "Aucune donnée extraite"**
- Vérifier que les PDF ne sont pas protégés par mot de passe
- Vérifier que le format des PDF correspond au format attendu

**Problème : "Erreur lors du traitement"**
- Vérifier que le fichier ZIP n'est pas corrompu
- Vérifier que les PDF sont bien lisibles

## 📧 Support

Pour toute question ou problème, contacter le service RH.

## 📄 Licence

Usage interne - Executive Relocations
