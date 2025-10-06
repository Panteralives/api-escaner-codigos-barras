
import streamlit as st
import requests
from PIL import Image

# Configuración de la API
API_BASE_URL = "http://localhost:8001/api/v1"

def get_headers():
    """Obtener headers con token de autenticación si está disponible"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def check_api_connection():
    """Verificar conexión con la API"""
    try:
        response = requests.get("http://localhost:8001/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def login(username, password):
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

def test_usb_scanner(timeout=15):
    """Probar scanner USB-HID"""
    try:
        response = requests.post(f"{API_BASE_URL}/usb-scanner/test?timeout={timeout}")
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
