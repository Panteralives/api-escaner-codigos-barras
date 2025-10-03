import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api.main import app
from src.db.init_db import init_database

client = TestClient(app)


class TestAPI:
    """Tests básicos para la API"""
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_redirect(self):
        """Test de redirección a docs"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Redirect
    
    def test_api_info(self):
        """Test del endpoint de información de la API"""
        response = client.get("/api/v1")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestProductos:
    """Tests para endpoints de productos"""
    
    def test_get_productos(self):
        """Test para obtener lista de productos"""
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_producto_existing(self):
        """Test para obtener un producto existente"""
        # Primero obtener la lista para usar un código real
        response = client.get("/api/v1/productos/")
        productos = response.json()
        
        if productos:
            codigo_barra = productos[0]["codigo_barra"]
            response = client.get(f"/api/v1/productos/{codigo_barra}")
            assert response.status_code == 200
            data = response.json()
            assert data["codigo_barra"] == codigo_barra
    
    def test_get_producto_not_found(self):
        """Test para producto no encontrado"""
        response = client.get("/api/v1/productos/999999999999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data["detail"]
    
    def test_get_categorias(self):
        """Test para obtener categorías"""
        response = client.get("/api/v1/productos/categorias/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuth:
    """Tests para autenticación"""
    
    def test_login_success(self):
        """Test de login exitoso con credenciales por defecto"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid(self):
        """Test de login con credenciales inválidas"""
        login_data = {
            "username": "invalid",
            "password": "invalid"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "error" in data["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test de endpoint protegido sin token"""
        product_data = {
            "codigo_barra": "1234567890123",
            "nombre": "Test Product",
            "precio": 1.0
        }
        response = client.post("/api/v1/productos/", json=product_data)
        # El sistema devuelve 403 (Forbidden) cuando no hay token
        assert response.status_code == 403


class TestScanner:
    """Tests para funcionalidad de escáner"""
    
    def test_camera_status(self):
        """Test para verificar estado de cámara"""
        response = client.get("/api/v1/scan/camera/status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert "camera_index" in data
        assert "message" in data
    
    def test_scan_image_without_file(self):
        """Test de escaneo sin archivo"""
        response = client.post("/api/v1/scan/image")
        assert response.status_code == 422  # Validation error
    
    def test_camera_stop(self):
        """Test para detener cámara"""
        response = client.post("/api/v1/scan/camera/stop")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v"])