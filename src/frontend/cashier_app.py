import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from PIL import Image
import io

# Configuración de la API
API_BASE_URL = "http://localhost:8001/api/v1"

# Configurar página específica para cajero
st.set_page_config(
    page_title="🛒 Sistema POS - Cajero",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def check_api_connection():
    """Verificar conexión con la API"""
    try:
        response = requests.get("http://localhost:8001/health")
        return response.status_code == 200
    except:
        return False

def get_headers():
    """Obtener headers con token de autenticación si está disponible"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def get_productos():
    """Obtener lista de productos"""
    try:
        response = requests.get(f"{API_BASE_URL}/productos/")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def scan_image(uploaded_file):
    """Escanear imagen subida"""
    try:
        files = {"file": ("image.jpg", uploaded_file, "image/jpeg")}
        response = requests.post(f"{API_BASE_URL}/scan/image", files=files)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def scan_camera():
    """Escanear desde cámara"""
    try:
        response = requests.post(f"{API_BASE_URL}/scan/camera")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def camera_status():
    """Verificar estado de la cámara"""
    try:
        response = requests.get(f"{API_BASE_URL}/scan/camera/status")
        return response.json()
    except Exception as e:
        return {"available": False, "message": f"Error: {str(e)}"}

# Funciones para scanner USB-HID
def usb_scanner_status():
    """Verificar estado del scanner USB-HID"""
    try:
        response = requests.get(f"{API_BASE_URL}/usb-scanner/status")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def start_usb_scanner():
    """Iniciar scanner USB-HID"""
    try:
        response = requests.post(f"{API_BASE_URL}/usb-scanner/start")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def stop_usb_scanner():
    """Detener scanner USB-HID"""
    try:
        response = requests.post(f"{API_BASE_URL}/usb-scanner/stop")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def get_recent_usb_scans(limit=10):
    """Obtener escaneos recientes del scanner USB"""
    try:
        response = requests.get(f"{API_BASE_URL}/usb-scanner/recent-scans?limit={limit}")
        return response.json()
    except Exception as e:
        return {"status": "error", "escaneos": []}

def main():
    """Función principal de la aplicación para cajero"""
    # Barra lateral para navegación - Versión Cajero
    st.sidebar.title("🛒 Sistema POS - Cajero")
    
    # Verificar conexión API
    if check_api_connection():
        st.sidebar.success("✅ Sistema Conectado")
    else:
        st.sidebar.error("❌ Sistema No Disponible")
        st.error("No se puede conectar con el sistema. Contacta al administrador.")
        st.stop()

    # Solo navegación para cajero (sin acceso administrativo)
    page = st.sidebar.selectbox(
        "Seleccionar Función",
        ["🏠 Inicio", "📱 Escanear Producto", "🔌 Scanner Físico", "📦 Consultar Productos"]
    )

    # Página principal
    st.title("🛒 Sistema POS - Terminal de Cajero")

    if page == "🏠 Inicio":
        st.subheader("🏠 Panel de Inicio")
        
        # 3 columnas como la estructura original
        col1, col2, col3 = st.columns(3)
        
        # Estadísticas básicas para cajero
        productos = get_productos()
        
        with col1:
            st.metric("📦 Productos Disponibles", len(productos))
            st.caption("Total de productos en sistema")
        
        with col2:
            camera_info = camera_status()
            camera_available = camera_info.get("available", False)
            st.metric("📷 Cámara", "✅ Lista" if camera_available else "❌ No disponible")
            st.caption("Estado del escáner de cámara")
        
        with col3:
            usb_status = usb_scanner_status()
            scanner_ok = usb_status.get("status") == "success"
            st.metric("🔌 Scanner USB", "✅ Disponible" if scanner_ok else "❌ Error")
            st.caption("Estado del escáner físico")
        
        # Estado de herramientas
        st.subheader("🛠️ Estado de Herramientas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📷 Escáner de Cámara**")
            if camera_available:
                st.success(f"✅ {camera_info.get('message', 'Cámara lista para usar')}")
            else:
                st.error(f"❌ {camera_info.get('message', 'Cámara no disponible')}")
                st.info("💡 Asegúrate de que la cámara esté conectada")
        
        with col2:
            st.write("**🔌 Escáner USB**")
            if scanner_ok:
                scanner_info = usb_status.get("scanner_info", {})
                if scanner_info.get("listening", False):
                    st.success("✅ Escáner activo y funcionando")
                else:
                    st.warning("🟠 Escáner disponible - Activar en 'Scanner Físico'")
            else:
                st.error(f"❌ {usb_status.get('message', 'Error en escáner USB')}")

        # Productos recientes (solo lectura para cajero)
        st.subheader("📋 Productos Recientes")
        if productos:
            df = pd.DataFrame(productos)
            # Mostrar solo información básica para cajero
            display_columns = ['codigo_barra', 'nombre', 'precio']
            if 'categoria' in df.columns:
                display_columns.append('categoria')
            st.dataframe(df[display_columns].head(8), use_container_width=True)
        else:
            st.info("No hay productos en el sistema")

    elif page == "📱 Escanear Producto":
        st.subheader("📱 Escanear Códigos de Barras")
        
        # Estructura original con tabs
        tab1, tab2 = st.tabs(["📷 Cámara", "🖼️ Imagen"])
        
        with tab1:
            st.write("### 📷 Escanear con Cámara")
            
            # Verificar estado de cámara
            camera_info = camera_status()
            if camera_info.get("available", False):
                st.success("✅ Cámara lista para escanear")
                
                if st.button("🔍 Escanear Ahora", type="primary", use_container_width=True):
                    with st.spinner("📸 Escaneando código..."):
                        result = scan_camera()
                        
                    # Mostrar resultado en estructura de 3 secciones
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    elif result.get("encontrado"):
                        # SECCIÓN 1: Código encontrado
                        st.success(f"✅ ¡Código detectado!")
                        
                        # SECCIÓN 2: Información del producto (3 columnas)
                        producto = result.get("producto")
                        if producto:
                            st.write("### 📦 Información del Producto")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("📋 Producto", producto['nombre'])
                                if producto.get("categoria"):
                                    st.caption(f"Categoría: {producto['categoria']}")
                            
                            with col2:
                                st.metric("💰 Precio", f"${producto['precio']:.2f}")
                                st.caption("Precio unitario")
                            
                            with col3:
                                st.metric("📊 Stock", f"{producto['stock']} unidades")
                                stock_status = "🟢 Disponible" if producto['stock'] > 0 else "🔴 Agotado"
                                st.caption(stock_status)
                            
                            # SECCIÓN 3: Detalles del escaneo
                            st.write("### 🔍 Detalles del Escaneo")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info(f"**Código:** {result['codigo_barra']}")
                                st.info(f"**Tipo:** {result['tipo_codigo']}")
                            
                            with col2:
                                st.info(f"**Escaneado:** {result['timestamp']}")
                                st.info("**Estado:** ✅ Encontrado en sistema")
                    else:
                        st.warning("⚠️ No se detectó código de barras")
                        st.info("💡 Asegúrate de que el código esté bien iluminado")
            else:
                st.error("❌ Cámara no disponible")
                st.info(camera_info.get("message", "Error desconocido"))
        
        with tab2:
            st.write("### 🖼️ Escanear desde Imagen")
            
            uploaded_file = st.file_uploader(
                "📎 Selecciona imagen con código de barras",
                type=['png', 'jpg', 'jpeg'],
                help="La imagen debe contener un código de barras visible"
            )
            
            if uploaded_file is not None:
                # Mostrar imagen
                image = Image.open(uploaded_file)
                st.image(image, caption="📷 Imagen cargada", use_column_width=True)
                
                if st.button("🔍 Procesar Imagen", type="primary", use_container_width=True):
                    with st.spinner("🔄 Analizando imagen..."):
                        result = scan_image(uploaded_file.getvalue())
                        
                    # Estructura de 3 secciones igual que cámara
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    elif result.get("encontrado"):
                        st.success(f"✅ ¡Código encontrado en imagen!")
                        
                        # Mostrar producto en 3 columnas
                        producto = result.get("producto")
                        if producto:
                            st.write("### 📦 Información del Producto")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("📋 Producto", producto['nombre'])
                                if producto.get("categoria"):
                                    st.caption(f"Categoría: {producto['categoria']}")
                            
                            with col2:
                                st.metric("💰 Precio", f"${producto['precio']:.2f}")
                                st.caption("Precio unitario")
                            
                            with col3:
                                st.metric("📊 Stock", f"{producto['stock']} unidades")
                                stock_status = "🟢 Disponible" if producto['stock'] > 0 else "🔴 Agotado"
                                st.caption(stock_status)
                        else:
                            st.warning("⚠️ Código detectado pero producto no encontrado")
                            st.write(f"**Código:** {result['codigo_barra']}")
                    else:
                        st.warning("⚠️ No se detectó código en la imagen")
                        st.info("💡 Consejos: Imagen clara, bien iluminada, sin reflejos")

    elif page == "🔌 Scanner Físico":
        st.subheader("🔌 Escáner Físico USB")
        
        # Verificar estado
        usb_status = usb_scanner_status()
        
        if usb_status.get("status") != "success":
            st.error(f"❌ Error de conexión: {usb_status.get('message', 'Error desconocido')}")
            st.stop()
        
        scanner_info = usb_status.get("scanner_info", {})
        
        if not scanner_info.get("keyboard_library", False):
            st.error("❌ Escáner USB no disponible")
            st.info("💻 Contacta al administrador para configurar el escáner")
            st.stop()
        
        # Control del scanner en 3 secciones
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("### 🎛️ Control")
            if scanner_info.get("listening", False):
                st.success("🎧 **ACTIVO**")
                st.write("Escáner funcionando")
                
                if st.button("⏹️ Detener", type="secondary", use_container_width=True):
                    with st.spinner("Deteniendo..."):
                        result = stop_usb_scanner()
                    
                    if result.get("status") == "success":
                        st.success("✅ Escáner detenido")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('message', 'Error')}")
            else:
                st.warning("🟠 **INACTIVO**")
                st.write("Escáner detenido")
                
                if st.button("▶️ Activar", type="primary", use_container_width=True):
                    with st.spinner("Activando..."):
                        result = start_usb_scanner()
                    
                    if result.get("status") == "success":
                        st.success("✅ Escáner activo")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('message', 'Error')}")
        
        with col2:
            st.write("### ℹ️ Estado")
            st.write(f"**Tipo:** USB-HID")
            st.write(f"**Estado:** {'🟢 Activo' if scanner_info.get('listening') else '🟠 Inactivo'}")
            st.write(f"**Longitud:** {scanner_info.get('min_barcode_length', 3)}-{scanner_info.get('max_barcode_length', 50)} chars")
            st.write(f"**Velocidad:** <{scanner_info.get('speed_threshold_ms', 100)} ms")
        
        with col3:
            st.write("### 🧪 Prueba")
            st.write("Verificar funcionamiento")
            
            if st.button("🧪 Probar", type="secondary", use_container_width=True):
                st.info("⏱️ Escanea un código en los próximos 15 segundos...")
                
                with st.spinner("Probando escáner..."):
                    try:
                        response = requests.post(f"{API_BASE_URL}/usb-scanner/test?timeout=15")
                        result = response.json()
                    except Exception as e:
                        result = {"status": "error", "message": str(e)}
                
                if result.get("status") == "success":
                    st.success(f"✅ ¡Funciona! Código: `{result.get('barcode_detected', '')}`")
                else:
                    st.warning(f"⚠️ {result.get('message', 'No se detectó código')}")
        
        # Escaneos recientes
        st.write("### 📊 Escaneos Recientes")
        
        scans_data = get_recent_usb_scans(5)
        
        if scans_data.get("status") == "success":
            escaneos = scans_data.get("escaneos", [])
            
            if escaneos:
                for i, escaneo in enumerate(escaneos, 1):
                    with st.container():
                        if escaneo.get("encontrado"):
                            producto = escaneo.get("producto", {})
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.success(f"✅ **{producto.get('nombre', 'Sin nombre')}**")
                                st.caption(f"Código: {escaneo.get('codigo_barra', '')}")
                            
                            with col2:
                                st.write(f"💰 ${producto.get('precio', 0):.2f}")
                                st.caption("Precio")
                            
                            with col3:
                                st.write(f"📊 {producto.get('stock', 0)} unid.")
                                st.caption("Stock")
                        else:
                            st.warning(f"⚠️ Código no encontrado: `{escaneo.get('codigo_barra', '')}`")
            else:
                st.info("📝 No hay escaneos recientes")
        else:
            st.error("❌ Error obteniendo escaneos")

    elif page == "📦 Consultar Productos":
        st.subheader("📦 Consultar Productos")
        
        productos = get_productos()
        
        if productos:
            st.success(f"📊 **{len(productos)} productos** en el sistema")
            
            # Buscador simple
            search = st.text_input("🔍 Buscar producto", placeholder="Nombre o código...")
            
            # Filtrar productos
            if search:
                filtered = [p for p in productos if 
                           search.lower() in p.get('nombre', '').lower() or 
                           search in str(p.get('codigo_barra', ''))]
            else:
                filtered = productos
            
            # Mostrar en tabla formato cajero
            if filtered:
                df = pd.DataFrame(filtered)
                
                # Preparar datos para mostrar
                display_df = pd.DataFrame({
                    'Código': df['codigo_barra'],
                    'Producto': df['nombre'],
                    'Precio': df['precio'].apply(lambda x: f"${x:.2f}"),
                    'Stock': df['stock'].apply(lambda x: f"{x} unid."),
                })
                
                if 'categoria' in df.columns:
                    display_df['Categoría'] = df['categoria']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                if search:
                    st.info(f"📋 Mostrando {len(filtered)} de {len(productos)} productos")
            else:
                st.warning("⚠️ No se encontraron productos con esa búsqueda")
        else:
            st.info("📝 No hay productos registrados en el sistema")

if __name__ == "__main__":
    main()