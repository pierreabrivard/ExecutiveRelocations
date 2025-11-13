import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Boîte à outils - Executive Relocations",
    page_icon="🧰",
    layout="wide"
)

# Contenu principal
st.markdown("### Bienvenue sur la boîte à outils d'Executive Relocations")

# Section informative
st.info("💡 **Sélectionnez une application dans le menu de gauche.**")

# Ajouter une section avec les catégories d'applications
st.markdown("### 📋 Applications")

st.markdown("#### Ressources Humaines")
st.markdown("- 🤒 **Extraction des bordereaux d'arrêts maladie** : Extrait automatiquement les informations des bordereaux d'arrêts maladie au format PDF")