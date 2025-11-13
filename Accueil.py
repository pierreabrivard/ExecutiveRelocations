import streamlit as st
import requests

# Configuration de la page
st.set_page_config(
    page_title="Boîte à outils - Executive Relocations",
    page_icon="🧰",
    layout="wide"
)

# Fonction pour récupérer la météo
def get_weather(city="Paris"):
    """Récupère les données météo pour une ville donnée"""
    try:
        # API OpenWeatherMap (gratuite)
        # Note : Pour une utilisation en production, il faudrait une clé API
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

# Contenu principal
st.markdown("### Bienvenue sur la boîte à outils Executive Relocations")

# Section informative
st.info("💡 **Sélectionnez une application dans le menu de gauche.**")

st.markdown("---")

st.markdown("### 🌤️ Météo à Gennevilliers")

# Sélection de la ville
ville = "Gennevilliers"

meteo = get_weather(ville)

if meteo:
    st.metric(
        label="Température",
        value=f"{meteo['temp']}°C"
    )
else:
    st.info("⏳ Chargement de la météo...")