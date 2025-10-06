
import streamlit as st
import pandas as pd
from utils import (
    check_api_connection, 
    login, 
    logout, 
    get_productos, 
    camera_status, 
    usb_scanner_status
)

st.set_page_config(
    page_title="Dashboard | Escáner de Códigos",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estado de Sesión ---
def init_session_state():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None

init_session_state()

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.title("🔍 Escáner de Códigos")

    if check_api_connection():
        st.success("✅ API Conectada")
    else:
        st.error("❌ API No Disponible")
        st.stop()

    st.subheader("👤 Autenticación")

    if st.session_state.token:
        user_info = st.session_state.user_info or {}
        username = user_info.get('username', 'Usuario')
        st.success(f"Sesión activa: {username}")
        if st.button("Cerrar Sesión"):
            logout()
            st.rerun()
    else:
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("Iniciar Sesión"):
                success, message = login(username, password)
                if success:
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    st.markdown("**Escáner de Códigos v2.0**")
    st.markdown("Interfaz Multi-Página")

# --- Página Principal (Dashboard) ---
st.title("🏠 Dashboard Principal")
st.write("Bienvenido al panel de control del sistema de escáner de códigos de barras.")

if not st.session_state.token:
    st.warning("Por favor, inicie sesión para ver el contenido.")
    st.stop()

col1, col2, col3 = st.columns(3)

# Métricas Principales
productos = get_productos()

with col1:
    st.metric("Productos Registrados", len(productos))

with col2:
    camera_info = camera_status()
    st.metric("Cámara", "Disponible" if camera_info.get("available") else "No Disponible")

with col3:
    auth_status = "Autenticado" if st.session_state.token else "No Autenticado"
    st.metric("Estado de Sesión", auth_status)

st.divider()

# Estado de los Módulos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📷 Estado de la Cámara")
    camera_info = camera_status()
    if camera_info.get("available"):
        st.success(f"✅ {camera_info.get('message', 'Cámara lista')}")
        st.info(f"Índice de cámara: {camera_info.get('camera_index', 0)}")
    else:
        st.error(f"❌ {camera_info.get('message', 'Cámara no disponible')}")

with col2:
    st.subheader("🔌 Estado del Scanner USB")
    usb_status = usb_scanner_status()
    if usb_status.get("status") == "success":
        scanner_info = usb_status.get("scanner_info", {})
        if scanner_info.get("listening"):
            st.success("✅ Scanner USB activo")
        else:
            st.warning("🟠 Scanner USB disponible pero inactivo")
    else:
        st.error(f"❌ {usb_status.get('message', 'Error')}")


st.divider()

# Productos Recientes
st.subheader("📦 Productos Recientes")
if productos:
    df = pd.DataFrame(productos)
    st.dataframe(df[['codigo_barra', 'nombre', 'precio', 'categoria']].head(5), use_container_width=True)
else:
    st.info("No hay productos registrados para mostrar.")
