
import streamlit as st
from PIL import Image
from utils import camera_status, scan_camera, scan_image

st.set_page_config(page_title="Escanear Códigos", page_icon="📱", layout="wide")

st.title("Escanear Códigos de Barras")

if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    st.warning("Por favor, inicie sesión para acceder a esta página.")
    st.stop()

tab1, tab2 = st.tabs(["📷 Desde Cámara", "🖼️ Desde Imagen"])

with tab1:
    st.write("### Escanear desde Cámara USB")
    
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
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", use_column_width=True)
        
        if st.button("🔍 Escanear Imagen", type="primary"):
            with st.spinner("Procesando imagen..."):
                result = scan_image(uploaded_file.getvalue())
                
            if "error" in result:
                st.error(f"Error: {result['error']}")
            elif result.get("encontrado"):
                st.success(f"✅ Código encontrado: {result['codigo_barra']}")
                
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
