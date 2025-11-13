import fitz  # PyMuPDF
import re
from datetime import datetime

def extraire_donnees_pdf(chemin_pdf):
    """
    Extrait les données d'un bordereau IJSS au format PDF
    Gère plusieurs lignes de prestations et retourne une liste de dictionnaires
    
    Args:
        chemin_pdf: Chemin vers le fichier PDF
        
    Returns:
        list: Liste de dictionnaires contenant les données extraites (une entrée par période)
    """
    try:
        # Ouvrir le PDF
        doc = fitz.open(chemin_pdf)
        
        # Extraire le texte de toutes les pages
        texte_complet = ""
        for page in doc:
            texte_complet += page.get_text()
        
        doc.close()
        
        # Extraire les informations communes
        date_paiement = ""
        beneficiaire = ""
        montant_net_total = "0,00 €"
        
        # 1. Date de paiement (Journée du JJ/MM/AAAA)
        match_date_paiement = re.search(r'Journée du (\d{2}/\d{2}/\d{4})', texte_complet)
        if match_date_paiement:
            date_paiement = match_date_paiement.group(1)
        
        # 2. Bénéficiaire (après "Détail des prestations pour")
        match_beneficiaire = re.search(r'Détail des prestations pour (.+?)(?:\n)', texte_complet)
        if match_beneficiaire:
            beneficiaire = match_beneficiaire.group(1).strip()
        
        # 3. Total net (dernière ligne avec "Total :")
        match_total = re.search(r'Total\s*:\s*([\d,]+)\s*€', texte_complet)
        if match_total:
            montant_net_total = f"{match_total.group(1)} €"
        
        # 4. Extraire toutes les lignes de prestations
        liste_donnees = []
        
        # Pattern pour lignes avec période (JJ/MM/AAAA au JJ/MM/AAAA)
        pattern_avec_periode = r'(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})\s+(I\.J\.\s*NORMALES|CARENCE|[A-Z\.\s]+?)\s+(\d+)\s+([\d,]+)\s*€\s+([\d,]+)\s*€'
        matches_periode = re.finditer(pattern_avec_periode, texte_complet)
        
        for match in matches_periode:
            donnees = {
                'Date de paiement': date_paiement,
                'Bénéficiaire': beneficiaire,
                'Date du': match.group(1),
                'Date au': match.group(2),
                'Nature de la prestation': match.group(3).strip(),
                'Quantité': int(match.group(4)),
                'Montant remboursé brut': f"{match.group(6)} €",
                'Montant remboursé net': montant_net_total
            }
            liste_donnees.append(donnees)
        
        # Si aucune ligne avec période trouvée, chercher les lignes CARENCE sans montant
        if not liste_donnees:
            pattern_carence = r'(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})\s+(CARENCE)\s+(\d+)\s+([\d,]+)\s*€\s+([\d,]+)\s*€'
            matches_carence = re.finditer(pattern_carence, texte_complet)
            
            for match in matches_carence:
                donnees = {
                    'Date de paiement': date_paiement,
                    'Bénéficiaire': beneficiaire,
                    'Date du': match.group(1),
                    'Date au': match.group(2),
                    'Nature de la prestation': match.group(3),
                    'Quantité': int(match.group(4)),
                    'Montant remboursé brut': "0,00 €",
                    'Montant remboursé net': "0,00 €"
                }
                liste_donnees.append(donnees)
        
        # Si toujours rien, retourner une ligne vide avec les infos de base
        if not liste_donnees:
            donnees = {
                'Date de paiement': date_paiement,
                'Bénéficiaire': beneficiaire,
                'Date du': "",
                'Date au': "",
                'Nature de la prestation': "",
                'Quantité': 0,
                'Montant remboursé brut': "0,00 €",
                'Montant remboursé net': montant_net_total
            }
            liste_donnees.append(donnees)
        
        return liste_donnees
    
    except Exception as e:
        print(f"Erreur lors de l'extraction du PDF {chemin_pdf}: {str(e)}")
        return None

def nettoyer_montant(montant_str):
    """Convertit une chaîne de montant en float"""
    try:
        return float(montant_str.replace('€', '').replace(',', '.').strip())
    except:
        return 0.0

def formater_date(date_str):
    """Formate une date au format JJ/MM/AAAA"""
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_str
