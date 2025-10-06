
import streamlit as st
import requests
from utils import get_productos, get_headers

st.set_page_config(page_title="Gestión de Productos", page_icon="📦", layout="wide")

st.title("Gestión de Productos")

if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    st.warning("Por favor, inicie sesión para acceder a esta página.")
    st.stop()

productos = get_productos()

tab1, tab2 = st.tabs(["📋 Lista de Productos", "➕ Agregar Producto"])

with tab1:
    if productos:
        col1, col2 = st.columns(2)
        
        with col1:
            categorias = list(set(p.get("categoria", "Sin categoría") for p in productos))
            categoria_filter = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)
        
        with col2:
            search_term = st.text_input("Buscar por nombre", placeholder="Ej: Coca Cola")
        
        productos_filtrados = productos
        
        if categoria_filter != "Todas":
            productos_filtrados = [p for p in productos_filtrados if p.get("categoria") == categoria_filter]
        
        if search_term:
            productos_filtrados = [
                p for p in productos_filtrados 
                if search_term.lower() in p.get("nombre", "").lower()
            ]
        
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
                    
                    response = requests.post(f"{st.secrets.api.url}/productos/", 
                                           json=data, headers=headers)
                    
                    if response.status_code == 201:
                        st.success("✅ Producto agregado correctamente")
                    else:
                        error = response.json()
                        st.error(f"Error: {error.get('detail', 'Error desconocido')}")
                
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")
