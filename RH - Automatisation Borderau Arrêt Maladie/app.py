import streamlit as st
import zipfile
import io
import pandas as pd
from pathlib import Path
import tempfile
import os
from pdf_extractor import extraire_donnees_pdf

# Configuration de la page
st.set_page_config(
    page_title="Extracteur IJSS",
    page_icon="📄",
    layout="centered"
)

# Initialisation de l'état de session
if 'etape' not in st.session_state:
    st.session_state.etape = 'upload'
if 'df_resultats' not in st.session_state:
    st.session_state.df_resultats = None

def reinitialiser():
    """Réinitialise l'application"""
    st.session_state.etape = 'upload'
    st.session_state.df_resultats = None
    st.rerun()

def traiter_zip(fichier_zip):
    """Traite le fichier ZIP et extrait les données de tous les PDFs"""
    donnees_extraites = []
    
    # Créer un dossier temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extraire le ZIP
        with zipfile.ZipFile(fichier_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Parcourir tous les fichiers PDF
        pdf_files = list(Path(temp_dir).rglob('*.pdf'))
        
        if not pdf_files:
            st.error("Aucun fichier PDF trouvé dans l'archive ZIP.")
            return None
        
        # Barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, pdf_path in enumerate(pdf_files):
            status_text.text(f"Traitement de {pdf_path.name}...")
            
            try:
                # Extraire les données du PDF (retourne une liste)
                liste_donnees = extraire_donnees_pdf(str(pdf_path))
                
                if liste_donnees:
                    # Ajouter toutes les lignes extraites
                    donnees_extraites.extend(liste_donnees)
                else:
                    st.warning(f"Impossible d'extraire les données de {pdf_path.name}")
            
            except Exception as e:
                st.warning(f"Erreur lors du traitement de {pdf_path.name}: {str(e)}")
            
            # Mettre à jour la barre de progression
            progress_bar.progress((idx + 1) / len(pdf_files))
        
        status_text.text("Traitement terminé!")
    
    if not donnees_extraites:
        st.error("Aucune donnée n'a pu être extraite des fichiers PDF.")
        return None
    
    # Créer un DataFrame
    df = pd.DataFrame(donnees_extraites)
    
    # Réorganiser les colonnes dans l'ordre souhaité
    colonnes_ordre = [
        'Date de paiement',
        'Bénéficiaire',
        'Nature de la prestation',
        'Date du',
        'Date au',
        'Quantité',
        'Montant remboursé brut',
        'Montant remboursé net'
    ]
    
    df = df[colonnes_ordre]
    
    return df

def convertir_df_en_excel(df):
    """Convertit un DataFrame en fichier Excel téléchargeable"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='IJSS')
        
        # Ajuster la largeur des colonnes
        worksheet = writer.sheets['IJSS']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
    
    output.seek(0)
    return output

# Interface principale
st.title("📄 Extracteur de Bordereaux IJSS")
st.markdown("### Application pour traiter les bordereaux de la Sécurité Sociale")

# Étape 1 : Upload du fichier
if st.session_state.etape == 'upload':
    st.markdown("---")
    st.subheader("1️⃣ Uploader votre fichier ZIP")
    st.info("📦 Sélectionnez un fichier ZIP contenant les bordereaux PDF de la Sécurité Sociale")
    
    fichier_zip = st.file_uploader(
        "Choisir un fichier ZIP",
        type=['zip'],
        help="Le fichier doit contenir des bordereaux PDF d'Indemnités Journalières"
    )
    
    if fichier_zip is not None:
        st.success(f"✅ Fichier chargé : {fichier_zip.name}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Extraire les données", type="primary", use_container_width=True):
                with st.spinner("Extraction des données en cours..."):
                    df = traiter_zip(fichier_zip)
                    
                    if df is not None:
                        st.session_state.df_resultats = df
                        st.session_state.etape = 'resultats'
                        st.rerun()

# Étape 2 : Affichage des résultats et téléchargement
elif st.session_state.etape == 'resultats':
    st.markdown("---")
    st.subheader("2️⃣ Résultats de l'extraction")
    
    df = st.session_state.df_resultats
    
    # Afficher les statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Nombre de lignes", len(df))
    with col2:
        montant_total = df['Montant remboursé net'].astype(str).str.replace('€', '').str.replace(',', '.').astype(float).sum()
        st.metric("💰 Montant total net", f"{montant_total:.2f} €")
    with col3:
        nb_beneficiaires = df['Bénéficiaire'].nunique()
        st.metric("👥 Bénéficiaires", nb_beneficiaires)
    
    # Afficher le tableau
    st.markdown("### 📊 Aperçu des données extraites")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Bouton de téléchargement
    st.markdown("---")
    st.subheader("3️⃣ Télécharger le fichier Excel")
    
    excel_file = convertir_df_en_excel(df)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=excel_file,
            file_name="bordereaux_IJSS_extraits.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    
    # Lien pour recommencer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Recommencer", use_container_width=True):
            reinitialiser()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    💡 Application développée pour faciliter le traitement des bordereaux IJSS<br>
    En cas de problème, vérifiez que vos fichiers PDF sont bien formatés
    </div>
    """,
    unsafe_allow_html=True
)
