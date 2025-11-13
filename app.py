import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Boîte à outils - Executive Relocations",
    page_icon="🧰",
    layout="wide"
)

# Titre principal
st.title("🧰 Boîte à outils - Executive Relocations")

# Contenu principal
st.markdown("### Bienvenue sur la boîte à outils Executive Relocations")
st.write("Sélectionnez une application dans le menu de gauche pour commencer.")

# Afficher des informations ou statistiques
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Applications disponibles", value="1")

with col2:
    st.metric(label="Catégories", value="1")

with col3:
    st.metric(label="En développement", value="0")

st.markdown("---")

# Section informative
st.info("💡 **Astuce** : Utilisez le menu latéral pour naviguer entre les différentes applications.")

# Ajouter une section avec les catégories d'applications
st.markdown("### 📋 Applications disponibles")

st.markdown("#### Ressources Humaines")
st.markdown("- 🤒 **Extraction des bordereaux d'arrêts maladie** : Extrait automatiquement les informations des bordereaux d'arrêts maladie au format PDF")