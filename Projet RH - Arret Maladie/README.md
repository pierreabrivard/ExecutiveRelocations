# Extraction des paiements CPAM

Application Streamlit permettant d'extraire automatiquement les informations de paiement depuis les relevés CPAM (Caisse Primaire d'Assurance Maladie) et de générer un fichier Excel consolidé.

## Fonctionnalités

- Téléchargement d'une archive ZIP contenant des relevés CPAM au format PDF 📁
- Extraction de la date de paiement, du bénéficiaire, des périodes, du type de prestation et des montants 📄
- Gestion des erreurs document par document, avec un récapitulatif des réussites et des échecs ❌✅
- Génération d'un fichier Excel exportable contenant l'ensemble des données extraites 📊
- Interface Streamlit responsive avec indicateurs d'avancement et option de réinitialisation

## Utilisation

1. Regroupez vos relevés CPAM (PDF) dans un fichier ZIP.
2. Lancez l'application Streamlit (`streamlit run app.py`).
3. Importez votre fichier ZIP via l'interface.
4. Cliquez sur « Extraire les données » pour lancer l'analyse.
5. Téléchargez le fichier Excel généré depuis l'application.

## Installation locale

```bash
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement sur Streamlit Cloud

1. Poussez ce projet sur un dépôt Git (GitHub, GitLab…).
2. Sur Streamlit Cloud, créez une nouvelle application en pointant vers ce dépôt.
3. Sélectionnez `app.py` comme fichier principal.
4. Streamlit installera automatiquement les dépendances listées dans `requirements.txt`.
5. Configurez, si nécessaire, les secrets dans `.streamlit/secrets.toml` (non obligatoire pour cette application).

L'application est alors accessible en ligne aux utilisateurs autorisés.

