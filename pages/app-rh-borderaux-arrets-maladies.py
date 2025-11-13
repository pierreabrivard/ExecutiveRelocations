import streamlit as st
import time
import zipfile
from io import BytesIO
import pdfplumber
import pandas as pd
import re

# Afficher un loader au démarrage
with st.spinner("Chargement de l'application..."):
    time.sleep(0.5)

def extraire_info_pdf(pdf_bytes):
    """Extrait les informations d'un PDF"""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            # Lire la première page
            page = pdf.pages[0]
            text = page.extract_text()
            
            # Extraire Date du paiement (après "Journée du ")
            date_paiement = ''
            match = re.search(r'Journée du\s+(\d{2}/\d{2}/\d{4})', text)
            if match:
                date_paiement = match.group(1)
            
            # Extraire Matricule (après "Matricule : ")
            matricule = ''
            match = re.search(r'Matricule\s*:\s*(\S+)', text)
            if match:
                matricule = match.group(1)
            
            # Extraire Nom du bénéficiaire (après "Bénéficiaire : ")
            nom_beneficiaire = ''
            match = re.search(r'Bénéficiaire\s*:\s*([^\n]+)', text)
            if match:
                nom_beneficiaire = match.group(1).strip()
            
            # Extraire Montant net (après "Total : ")
            montant_net = ''
            match = re.search(r'Total\s*:\s*([0-9,]+(?:\.\d{2})?)\s*€?', text)
            if match:
                montant_net = match.group(1)
            
            # Trouver toutes les lignes avec dates, nature, quantité et montants
            # Pattern pour trouver les lignes du tableau avec quantité différente de 0
            # Format: dd/mm/yyyy au dd/mm/yyyy Nature Quantité PrixUnitaire MontantRemboursé
            pattern = r'(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})\s+([^\d]+?)\s+(\d+)\s+([0-9,]+(?:\.\d{2})?)\s*€?\s+([0-9,]+(?:\.\d{2})?)\s*€?'
            
            lignes = []
            for match in re.finditer(pattern, text):
                quantite = int(match.group(4))
                # Ne garder que les lignes avec quantité > 0
                if quantite > 0:
                    lignes.append({
                        'Date du paiement': date_paiement,
                        'Matricule': matricule,
                        'Nom du bénéficiaire': nom_beneficiaire,
                        'Date du': match.group(1),
                        'Date de fin': match.group(2),
                        'Nature de la prestation': match.group(3).strip(),
                        'Quantité': str(quantite),
                        'Montant brut': match.group(6),  # Dernier montant = Montant remboursé
                        'Montant net': montant_net
                    })
            
            return lignes if lignes else None
    except Exception as e:
        st.error(f"Erreur lors de l'extraction : {str(e)}")
        return None

# Titre
st.title("Bonjour Elise :)")

# Texte explicatif
st.write("Télécharge le dossier .zip avec l'ensemble des bordereaux d'arrêts maladies")

# Input de téléchargement
uploaded_file = st.file_uploader("Choisir un fichier", type=['zip'])

# Message de confirmation si un fichier est téléchargé
if uploaded_file is not None:
    st.success("Parfait 🥳")
    time.sleep(2)
    
    with st.spinner("Extraction en cours..."):
        # Lire le fichier zip
        with zipfile.ZipFile(BytesIO(uploaded_file.read())) as zip_file:
            # Récupérer la liste des noms de fichiers
            file_names = zip_file.namelist()
        
        time.sleep(1)  # Simulation du temps d'extraction
    
    # Afficher la liste des fichiers avec icônes
    st.write("**Fichiers trouvés dans le dossier :**")
    pdf_files = []
    for file_name in file_names:
        if not file_name.endswith('/'):  # Ignorer les dossiers
            if file_name.lower().endswith('.pdf'):
                st.write(f"{file_name} -- ✅ OK")
                pdf_files.append(file_name)
            else:
                st.write(f"{file_name} -- ⛔ Ce fichier n'est pas un pdf")
    
    # Extraire les informations des PDFs
    if pdf_files:
        with st.spinner("Extraction des informations..."):
            donnees = []
            with zipfile.ZipFile(BytesIO(uploaded_file.getvalue())) as zip_file:
                for pdf_file in pdf_files:
                    pdf_bytes = zip_file.read(pdf_file)
                    lignes = extraire_info_pdf(pdf_bytes)
                    if lignes:
                        for ligne in lignes:
                            ligne['Nom du fichier'] = pdf_file
                            donnees.append(ligne)
            
            time.sleep(1)
        
        st.success("Extraction terminée !")
        
        # Afficher le tableau avec les données
        if donnees:
            st.write("**Informations extraites des bordereaux :**")
            df = pd.DataFrame(donnees)
            # Réorganiser les colonnes
            colonnes = ['Nom du fichier', 'Date du paiement', 'Matricule', 'Nom du bénéficiaire', 
                       'Date du', 'Date de fin', 'Nature de la prestation', 'Quantité', 
                       'Montant brut', 'Montant net']
            df = df[colonnes]
            st.dataframe(df, use_container_width=True)
            
            # Bouton de téléchargement Excel
            # Créer le fichier Excel en mémoire
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Bordereaux')
            output.seek(0)
            
            # Bouton de téléchargement
            st.download_button(
                label="Télécharger le fichier Excel",
                data=output,
                file_name="bordereaux_arrêts_maladies.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Aucune donnée n'a pu être extraite des PDF.")
    else:
        st.warning("Aucun fichier PDF trouvé dans le dossier.")