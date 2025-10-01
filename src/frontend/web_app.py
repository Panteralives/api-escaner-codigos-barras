#!/usr/bin/env python3
"""
Frontend web alternativo usando FastAPI con templates HTML
Reemplaza Streamlit que estaba causando problemas
"""

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import asyncio
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000/api/v1"

# Crear app FastAPI
app = FastAPI(title="Scanner Web Interface", description="Interfaz web para escáner de códigos")

# Configurar templates SIN CACHE para desarrollo
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
# Desactivar cache de templates para que siempre use la versión más reciente
templates = Jinja2Templates(directory=str(templates_dir))
templates.env.cache = {}

# Configurar archivos estáticos
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


async def check_api_connection():
    """Verificar conexión con la API backend"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://localhost:8000/health")
            return response.status_code == 200
    except:
        return False


async def get_productos():
    """Obtener lista de productos del backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/productos/")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
    return []


async def login_user(username: str, password: str):
    """Intentar login en el backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            data = {"username": username, "password": password}
            response = await client.post(f"{API_BASE_URL}/auth/login", data=data)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error = response.json()
                return {"success": False, "error": error.get("detail", "Error de autenticación")}
    except Exception as e:
        return {"success": False, "error": f"Error de conexión: {str(e)}"}


async def get_admin_token():
    """Obtener token de administrador para operaciones internas"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            data = {"username": "admin", "password": "admin123"}
            response = await client.post(f"{API_BASE_URL}/auth/login", data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]
    except Exception as e:
        print(f"Error obteniendo token admin: {e}")
    return None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal - Dashboard"""
    api_status = await check_api_connection()
    productos = await get_productos()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "api_status": api_status,
        "productos": productos,
        "total_productos": len(productos)
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesar login"""
    result = await login_user(username, password)
    
    if result["success"]:
        # En un caso real, aquí manejarías la sesión
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": result["error"]
        })


@app.get("/scan", response_class=HTMLResponse)
async def scan_page(request: Request):
    """Página de escaneo"""
    api_status = await check_api_connection()
    return templates.TemplateResponse("scan.html", {
        "request": request,
        "api_status": api_status
    })


@app.get("/productos", response_class=HTMLResponse)
async def productos_page(request: Request):
    """Página de productos"""
    productos = await get_productos()
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": productos
    })


@app.get("/status")
async def status():
    """Status de la aplicación web"""
    api_status = await check_api_connection()
    return {
        "web_status": "ok",
        "api_status": "connected" if api_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }


# Endpoints proxy para API del backend
@app.get("/api/productos")
async def api_productos():
    """Proxy para obtener productos del backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/productos/")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Error del backend")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")


@app.post("/api/productos")
async def api_create_producto(request: Request):
    """Proxy para crear productos en el backend"""
    try:
        # Obtener token de admin
        token = await get_admin_token()
        if not token:
            raise HTTPException(status_code=401, detail="Error de autenticación interna")
        
        data = await request.json()
        
        # Headers con autenticación
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/productos/",
                json=data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = {"detail": "Error del backend"}
                raise HTTPException(status_code=response.status_code, detail=error_detail)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")


@app.get("/api/camera/status")
async def api_camera_status():
    """Proxy para estado de cámara"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/scan/camera/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"available": False, "message": "Error verificando cámara"}
    except Exception as e:
        return {"available": False, "message": f"Error: {str(e)}"}


@app.get("/api/usb-scanner/status")
async def api_usb_scanner_status():
    """Proxy para estado del scanner USB"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/usb-scanner/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": "Error verificando scanner"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}


@app.get("/api/usb-scanner/recent-scans")
async def api_usb_scanner_recent_scans(limit: int = 10):
    """Proxy para escaneos recientes del scanner USB"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/usb-scanner/recent-scans?limit={limit}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "escaneos": []}
    except Exception as e:
        return {"status": "error", "escaneos": [], "message": f"Error: {str(e)}"}


@app.post("/api/scan/camera")
async def api_scan_camera():
    """Proxy para escaneo desde cámara"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:  # Más tiempo para escaneo
            response = await client.post(f"{API_BASE_URL}/scan/camera")
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json() if response.content else {"error": "Error escaneando"}
                return error_detail
    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}


@app.post("/api/scan/image")
async def api_scan_image(request: Request):
    """Proxy para escaneo de imagen subida"""
    try:
        # FastAPI maneja multipart/form-data automáticamente
        form = await request.form()
        file = form.get("file")
        
        if not file:
            raise HTTPException(status_code=400, detail="No se proporcionó archivo")
        
        # Preparar archivo para envío al backend
        files = {"file": (file.filename, await file.read(), file.content_type)}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/scan/image",
                files=files
            )
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json() if response.content else {"error": "Error escaneando imagen"}
                return error_detail
                
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Error procesando imagen: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    
    print("[WEB] Iniciando frontend web alternativo...")
    print("[INFO] Interfaz disponible en: http://localhost:8501")
    print("[INFO] Asegurate de que la API este ejecutandose en http://localhost:8000")
    print("-" * 50)
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8501,
        reload=True,
        log_level="info"
    )