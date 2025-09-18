import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import base64
from PIL import Image
import io

# Configuración de la API
API_BASE_URL = "http://localhost:8000/api/v1"

# Configurar página
st.set_page_config(
    page_title="Escáner de Códigos de Barras",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None


def get_headers():
    """Obtener headers con token de autenticación si está disponible"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers


def check_api_connection():
    """Verificar conexión con la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/../health")
        return response.status_code == 200
    except:
        return False


def login(username: str, password: str):
    """Iniciar sesión"""
    try:
        data = {"username": username, "password": password}
        response = requests.post(f"{API_BASE_URL}/auth/login", data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            
            # Obtener información del usuario
            headers = get_headers()
            user_response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
            if user_response.status_code == 200:
                st.session_state.user_info = user_response.json()
            
            return True, "Sesión iniciada correctamente"
        else:
            error = response.json()
            return False, error.get("detail", {}).get("error", "Error de autenticación")
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"


def logout():
    """Cerrar sesión"""
    st.session_state.token = None
    st.session_state.user_info = None


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


# Barra lateral para navegación
st.sidebar.title("🔍 Escáner de Códigos")

# Verificar conexión API
if check_api_connection():
    st.sidebar.success("✅ API Conectada")
else:
    st.sidebar.error("❌ API No Disponible")
    st.error("No se puede conectar con la API. Asegúrate de que esté ejecutándose en http://localhost:8000")
    st.stop()

# Sección de autenticación en sidebar
st.sidebar.subheader("👤 Autenticación")

if st.session_state.token:
    st.sidebar.success(f"Sesión activa: {st.session_state.user_info.get('username', 'Usuario')}")
    if st.sidebar.button("Cerrar Sesión"):
        logout()
        st.rerun()
else:
    with st.sidebar.form("login_form"):
        username = st.text_input("Usuario", placeholder="admin")
        password = st.text_input("Contraseña", type="password", placeholder="admin123")
        submit_button = st.form_submit_button("Iniciar Sesión")
        
        if submit_button:
            success, message = login(username, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

# Navegación principal
page = st.sidebar.selectbox(
    "Seleccionar Función",
    ["🏠 Dashboard", "📱 Escanear", "📦 Productos", "📊 Historial"]
)

# Página principal
st.title("🔍 Escáner de Códigos de Barras")

if page == "🏠 Dashboard":
    st.subheader("Panel Principal")
    
    col1, col2, col3 = st.columns(3)
    
    # Estadísticas básicas
    productos = get_productos()
    
    with col1:
        st.metric("Productos Registrados", len(productos))
    
    with col2:
        camera_info = camera_status()
        camera_available = camera_info.get("available", False)
        st.metric("Cámara", "Disponible" if camera_available else "No Disponible")
    
    with col3:
        auth_status = "Autenticado" if st.session_state.token else "No Autenticado"
        st.metric("Estado de Sesión", auth_status)
    
    # Estado de la cámara
    st.subheader("📷 Estado de la Cámara")
    if camera_available:
        st.success(f"✅ {camera_info.get('message', 'Cámara lista')}")
        st.info(f"Índice de cámara: {camera_info.get('camera_index', 0)}")
    else:
        st.error(f"❌ {camera_info.get('message', 'Cámara no disponible')}")
        st.info("💡 **Cómo conectar tu cámara:**")
        st.markdown("""
        1. Conecta una webcam USB a tu computadora
        2. Asegúrate de que no esté siendo usada por otra aplicación
        3. Reinicia la aplicación si es necesario
        4. Verifica que los drivers estén instalados
        """)
    
    # Productos recientes
    st.subheader("📦 Productos Recientes")
    if productos:
        df = pd.DataFrame(productos)
        st.dataframe(df[['codigo_barra', 'nombre', 'precio', 'categoria']].head(5), use_container_width=True)
    else:
        st.info("No hay productos registrados")

elif page == "📱 Escanear":
    st.subheader("Escanear Códigos de Barras")
    
    tab1, tab2 = st.tabs(["📷 Desde Cámara", "🖼️ Desde Imagen"])
    
    with tab1:
        st.write("### Escanear desde Cámara USB")
        
        # Verificar estado de cámara
        camera_info = camera_status()
        if camera_info.get("available", False):
            st.success("✅ Cámara disponible y lista para usar")
            
            if st.button("🔍 Escanear Ahora", type="primary"):
                with st.spinner("Escaneando código..."):
                    result = scan_camera()
                    
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                elif result.get("encontrado"):
                    st.success(f"✅ Código encontrado: {result['codigo_barra']}")
                    
                    # Mostrar información del producto
                    producto = result.get("producto")
                    if producto:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Información del Producto:**")
                            st.write(f"- **Nombre:** {producto['nombre']}")
                            st.write(f"- **Precio:** ${producto['precio']:.2f}")
                            st.write(f"- **Stock:** {producto['stock']} unidades")
                            if producto.get("categoria"):
                                st.write(f"- **Categoría:** {producto['categoria']}")
                        
                        with col2:
                            st.write("**Detalles del Escaneo:**")
                            st.write(f"- **Código:** {result['codigo_barra']}")
                            st.write(f"- **Tipo:** {result['tipo_codigo']}")
                            st.write(f"- **Escaneado:** {result['timestamp']}")
                else:
                    st.warning("⚠️ No se detectó ningún código de barras")
                    st.info("Asegúrate de que el código esté bien iluminado y enfocado")
        else:
            st.error("❌ Cámara no disponible")
            st.info(camera_info.get("message", "Error desconocido"))
    
    with tab2:
        st.write("### Subir Imagen para Escanear")
        
        uploaded_file = st.file_uploader(
            "Selecciona una imagen con código de barras",
            type=['png', 'jpg', 'jpeg'],
            help="La imagen debe contener un código de barras visible y legible"
        )
        
        if uploaded_file is not None:
            # Mostrar imagen
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagen subida", use_column_width=True)
            
            if st.button("🔍 Escanear Imagen", type="primary"):
                with st.spinner("Procesando imagen..."):
                    result = scan_image(uploaded_file.getvalue())
                    
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                elif result.get("encontrado"):
                    st.success(f"✅ Código encontrado: {result['codigo_barra']}")
                    
                    # Mostrar información del producto
                    producto = result.get("producto")
                    if producto:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Información del Producto:**")
                            st.write(f"- **Nombre:** {producto['nombre']}")
                            st.write(f"- **Precio:** ${producto['precio']:.2f}")
                            st.write(f"- **Stock:** {producto['stock']} unidades")
                            if producto.get("categoria"):
                                st.write(f"- **Categoría:** {producto['categoria']}")
                        
                        with col2:
                            st.write("**Detalles del Escaneo:**")
                            st.write(f"- **Código:** {result['codigo_barra']}")
                            st.write(f"- **Tipo:** {result['tipo_codigo']}")
                            st.write(f"- **Escaneado:** {result['timestamp']}")
                    else:
                        st.warning("⚠️ Código detectado pero producto no encontrado en la base de datos")
                        st.write(f"**Código:** {result['codigo_barra']}")
                        st.write(f"**Tipo:** {result['tipo_codigo']}")
                else:
                    st.warning("⚠️ No se detectó ningún código de barras en la imagen")
                    st.info("Consejos para mejorar la detección:")
                    st.markdown("""
                    - Asegúrate de que el código esté bien iluminado
                    - El código debe ser claramente visible y no estar distorsionado
                    - Evita reflejos o sombras sobre el código
                    - La imagen debe tener buena resolución
                    """)

elif page == "📦 Productos":
    st.subheader("Gestión de Productos")
    
    # Obtener productos
    productos = get_productos()
    
    tab1, tab2 = st.tabs(["📋 Lista de Productos", "➕ Agregar Producto"])
    
    with tab1:
        if productos:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                # Filtro por categoría
                categorias = list(set(p.get("categoria", "Sin categoría") for p in productos))
                categoria_filter = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)
            
            with col2:
                # Búsqueda por nombre
                search_term = st.text_input("Buscar por nombre", placeholder="Ej: Coca Cola")
            
            # Aplicar filtros
            productos_filtrados = productos
            
            if categoria_filter != "Todas":
                productos_filtrados = [p for p in productos_filtrados if p.get("categoria") == categoria_filter]
            
            if search_term:
                productos_filtrados = [
                    p for p in productos_filtrados 
                    if search_term.lower() in p.get("nombre", "").lower()
                ]
            
            # Mostrar productos en tarjetas
            for i in range(0, len(productos_filtrados), 2):
                col1, col2 = st.columns(2)
                
                for j, col in enumerate([col1, col2]):
                    if i + j < len(productos_filtrados):
                        producto = productos_filtrados[i + j]
                        
                        with col:
                            with st.container():
                                st.write(f"**{producto['nombre']}**")
                                st.write(f"Código: `{producto['codigo_barra']}`")
                                st.write(f"Precio: ${producto['precio']:.2f}")
                                st.write(f"Stock: {producto['stock']} unidades")
                                if producto.get("categoria"):
                                    st.write(f"Categoría: {producto['categoria']}")
                                if producto.get("descripcion"):
                                    st.write(f"*{producto['descripcion']}*")
                                st.divider()
        else:
            st.info("No hay productos registrados")
    
    with tab2:
        st.write("### Agregar Nuevo Producto")
        
        if not st.session_state.token:
            st.warning("⚠️ Debes iniciar sesión para agregar productos")
        else:
            with st.form("add_product_form"):
                codigo_barra = st.text_input("Código de Barras *", placeholder="7501000673209")
                nombre = st.text_input("Nombre del Producto *", placeholder="Coca Cola 600ml")
                precio = st.number_input("Precio *", min_value=0.01, value=1.0, step=0.01)
                descripcion = st.text_area("Descripción", placeholder="Descripción opcional del producto")
                stock = st.number_input("Stock Inicial", min_value=0, value=0)
                categoria = st.text_input("Categoría", placeholder="Ej: Bebidas")
                
                submit_button = st.form_submit_button("Agregar Producto", type="primary")
                
                if submit_button:
                    if not codigo_barra or not nombre:
                        st.error("El código de barras y nombre son obligatorios")
                    else:
                        try:
                            headers = get_headers()
                            data = {
                                "codigo_barra": codigo_barra,
                                "nombre": nombre,
                                "precio": precio,
                                "descripcion": descripcion if descripcion else None,
                                "stock": stock,
                                "categoria": categoria if categoria else None
                            }
                            
                            response = requests.post(f"{API_BASE_URL}/productos/", 
                                                   json=data, headers=headers)
                            
                            if response.status_code == 201:
                                st.success("✅ Producto agregado correctamente")
                                st.rerun()
                            else:
                                error = response.json()
                                st.error(f"Error: {error.get('detail', 'Error desconocido')}")
                        
                        except Exception as e:
                            st.error(f"Error de conexión: {str(e)}")

elif page == "📊 Historial":
    st.subheader("Historial de Escaneos")
    st.info("🚧 Funcionalidad en desarrollo. Pronto podrás ver el historial completo de escaneos.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.markdown("**Escáner de Códigos v1.0**")
st.sidebar.markdown("Desarrollado con Python + FastAPI + Streamlit")