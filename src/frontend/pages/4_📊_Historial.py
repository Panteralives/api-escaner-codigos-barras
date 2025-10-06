
import streamlit as st

st.set_page_config(page_title="Historial de Escaneos", page_icon="📊", layout="wide")

st.title("Historial de Escaneos")

if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    st.warning("Por favor, inicie sesión para acceder a esta página.")
    st.stop()

st.info("🚧 Funcionalidad en desarrollo. Pronto podrás ver el historial completo de escaneos.")
