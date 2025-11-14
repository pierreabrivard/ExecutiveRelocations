import streamlit as st
import requests

# Config
st.set_page_config(
    page_title="Boîte à outils - Executive Relocations",
    page_icon="🧰",
    layout="wide"
)

# Config Météo
def get_weather(city="Gennevilliers"):
    """Récupère les données météo pour une ville donnée"""
    try:
        # API OpenWeatherMap
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            return {
                'temp': current['temp_C'],
                'description': current['lang_fr'][0]['value'] if 'lang_fr' in current else current['weatherDesc'][0]['value'],
                'humidity': current['humidity'],
                'wind': current['windspeedKmph']
            }
    except:
        return None
    return None

# Titre
st.markdown("### Bienvenue sur la boîte à outils d'Executive Relocations")

# Information
st.info("⇽ **Sélectionnez une application dans le menu de gauche.**")

st.markdown("---")

st.markdown("### 🌤️ Météo à Gennevilliers")

# Ville
ville = "Gennevilliers"

meteo = get_weather(ville)

if meteo:
    st.metric(
        label="Température",
        value=f"{meteo['temp']}°C"
    )
else:
    st.info("⏳ Chargement de la météo...")

st.markdown("---")

st.markdown("### Dernières modifications")
st.markdown("• Commit 14112025-1416 • RH - Bordereaux Arrets Maladie -- Modification du pattern pour prendre en compte les montants avec espace (pour les milliers)")
st.markdown("• Commit 14112025-1416 • RH - Bordereaux Arrets Maladie -- Ajout d'un second parttern pour la ligne des Totaux (nouvelle ligne)")
st.markdown("• Commit 14112025-1416 • RH - Bordereaux Arrets Maladie -- Mise en forme des colonnes de date au format date dans le fichier excel")
st.markdown("• Commit 14112025-1416 • RH - Bordereaux Arrets Maladie -- Mise en forme des colonnes de montants au format numériques avec 2 décimales dans le fichier excel")
st.markdown("• Commit 14112025-1416 • RH - Bordereaux Arrets Maladie -- Mise en forme des entêtes de colonnes avec filtres dans le fichier excel")
