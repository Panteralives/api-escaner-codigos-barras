
import streamlit as st
from utils import (
    usb_scanner_status, 
    start_usb_scanner, 
    stop_usb_scanner, 
    test_usb_scanner, 
    get_recent_usb_scans
)

st.set_page_config(page_title="Scanner USB", page_icon="🔌", layout="wide")

st.title("Scanner USB-HID (Lector de Códigos como Teclado)")

if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    st.warning("Por favor, inicie sesión para acceder a esta página.")
    st.stop()

usb_status = usb_scanner_status()
if usb_status.get("status") != "success":
    st.error(f"❌ Error de conexión: {usb_status.get('message', 'Error desconocido')}")
    st.stop()

scanner_info = usb_status.get("scanner_info", {})

if not scanner_info.get("keyboard_library", False):
    st.error("❌ Librería 'keyboard' no disponible")
    st.info("💻 **Para activar el scanner USB:**")
    st.code("pip install keyboard")
    st.warning("⚠️ Este programa necesita ejecutarse como Administrador para funcionar")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔍 Control", "📊 Escaneos Recientes", "⚙️ Configuración"])

with tab1:
    st.write("### Control del Scanner USB")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if scanner_info.get("listening", False):
            st.success("🎧 Scanner ACTIVO y escuchando")
            st.write("El scanner está capturando códigos automáticamente")
            
            if st.button("⏹️ Detener Scanner", type="secondary"):
                with st.spinner("Deteniendo scanner..."):
                    result = stop_usb_scanner()
                
                if result.get("status") == "success":
                    st.success(result.get("message", "Scanner detenido"))
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('message', 'Error desconocido')}")
        else:
            st.warning("🟠 Scanner INACTIVO")
            st.write("Haz clic en 'Iniciar' para activar la detección automática")
            
            if st.button("▶️ Iniciar Scanner", type="primary"):
                with st.spinner("Iniciando scanner..."):
                    result = start_usb_scanner()
                
                if result.get("status") == "success":
                    st.success(result.get("message", "Scanner iniciado"))
                    st.info("🎯 **Instrucciones:**")
                    for instruction in result.get("instructions", []):
                        st.write(f"- {instruction}")
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('message', 'Error desconocido')}")
    
    with col2:
        st.write("**Información del Scanner:**")
        st.write(f"- **Tipo:** {scanner_info.get('type', 'USB-HID')}")
        st.write(f"- **Estado:** {'Activo' if scanner_info.get('listening') else 'Inactivo'}")
        st.write(f"- **Longitud mínima:** {scanner_info.get('min_barcode_length', 3)} caracteres")
        st.write(f"- **Longitud máxima:** {scanner_info.get('max_barcode_length', 50)} caracteres")
        st.write(f"- **Velocidad:** <{scanner_info.get('speed_threshold_ms', 100)} ms entre caracteres")
    
    st.write("### 🧪 Probar Scanner")
    st.write("Usa esta función para verificar que tu scanner funciona correctamente.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        timeout = st.slider("Tiempo de espera (segundos)", 5, 60, 15)
    
    with col2:
        if st.button("🧪 Probar Ahora", type="secondary"):
            st.info(f"⏱️ Esperando código por {timeout} segundos... ¡Escanea ahora!")
            
            with st.spinner(f"Probando scanner por {timeout} segundos..."):
                result = test_usb_scanner(timeout)
            
            if result.get("status") == "success":
                st.success(f"✅ ¡Scanner funciona perfectamente!")
                st.write(f"📷 **Código detectado:** `{result.get('barcode_detected', '')}`")
            elif result.get("status") == "warning":
                st.warning(result.get("message", "No se detectó código"))
                st.info("💡 **Sugerencias:**")
                for suggestion in result.get("suggestions", []):
                    st.write(f"- {suggestion}")
            else:
                st.error(f"Error en la prueba: {result.get('message', 'Error desconocido')}")

with tab2:
    st.write("### Escaneos Recientes del Scanner USB")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        limit = st.selectbox("Mostrar últimos:", [5, 10, 20, 50], index=1)
    
    with col2:
        if st.button("🔄 Actualizar"):
            st.rerun()
    
    scans_data = get_recent_usb_scans(limit)
    
    if scans_data.get("status") == "success":
        escaneos = scans_data.get("escaneos", [])
        
        if escaneos:
            st.success(f"📊 Mostrando {len(escaneos)} escaneos recientes")
            
            for i, escaneo in enumerate(escaneos, 1):
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if escaneo.get("encontrado"):
                            producto = escaneo.get("producto", {})
                            st.success(f"✅ **{producto.get('nombre', 'Producto sin nombre')}**")
                            st.write(f"Código: `{escaneo.get('codigo_barra', '')}`")
                            st.write(f"Precio: ${producto.get('precio', 0):.2f} | Stock: {producto.get('stock', 0)}")
                            if producto.get("categoria"):
                                st.write(f"Categoría: {producto.get('categoria')}")
                        else:
                            st.warning(f"⚠️ **Código no encontrado**")
                            st.write(f"Código: `{escaneo.get('codigo_barra', '')}`")
                    
                    with col2:
                        timestamp = escaneo.get('timestamp', '')
                        if timestamp:
                            st.write(f"🕐 {timestamp}")
                        st.write(f"🔌 {escaneo.get('tipo_codigo', 'USB-HID')}")
                    
                    st.divider()
        else:
            st.info("📋 No hay escaneos recientes del scanner USB")
            st.write("Los escaneos aparecerán aquí cuando uses el scanner.")
    else:
        st.error(f"Error obteniendo escaneos: {scans_data.get('message', 'Error desconocido')}")

with tab3:
    st.write("### Configuración del Scanner")
    
    st.info("🔧 **Configuración Actual del Scanner USB-HID**")
    
    st.write("### 📜 Guía de Uso")
    st.markdown("""
    **¿Cómo funciona el Scanner USB-HID?**
    
    1. 🔌 **Conecta tu scanner USB** - La mayoría de scanners modernos funcionan como un teclado
    2. ▶️ **Inicia el scanner** - Haz clic en "Iniciar Scanner" en la pestaña Control
    3. 📷 **Escanea códigos** - Simplemente apunta y escanea cualquier código de barras
    4. ✅ **Revisa los resultados** - Los productos se detectan automáticamente
    
    **Consejos importantes:**
    - 🔑 Ejecuta la aplicación como Administrador
    - 💻 Cierra otras aplicaciones que puedan usar el teclado
    - ⚡ Los scanners escriben muy rápido (< 100ms entre caracteres)
    - 🔄 Si no funciona, reinicia el scanner desde el Control
    """)
