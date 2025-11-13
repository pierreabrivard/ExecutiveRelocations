# Test Local de l'Application

## Installer les dépendances

```bash
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse : http://localhost:8501

## Créer un ZIP de test

Pour tester l'application, créez un dossier avec quelques PDFs de bordereaux IJSS, puis :

### Sur Windows :
1. Sélectionner le dossier
2. Clic droit → "Envoyer vers" → "Dossier compressé"

### Sur Mac :
1. Sélectionner le dossier
2. Clic droit → "Compress"

### Sur Linux :
```bash
zip -r bordereaux.zip dossier_des_pdfs/
```

## Tests automatisés

Pour tester l'extraction sans lancer l'interface :

```bash
python test_extraction.py
```

Ce script testera l'extraction sur les PDFs d'exemple et créera un fichier Excel de test.
