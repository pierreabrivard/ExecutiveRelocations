import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Boîte à outils - Executive Relocations",
    page_icon="🧰",
    layout="wide"
)

# Créer la sidebar (menu latéral)
with st.sidebar:
    st.header("Applications")
    st.markdown("---")
    
    # Catégorie Ressources Humaines
    st.subheader("Ressources Humaines")
    
    if st.button("🤒 Bordereaux d'arrêts maladie", use_container_width=True):
        st.switch_page("app-rh-borderaux-arrets-maladies.py")
    
    st.markdown("---")


# Contenu principal
st.markdown("### Boîte à outils d'Executive Relocations")
st.info("💡 **Sélectionnez une application dans le menu de gauche.**")