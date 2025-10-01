#!/usr/bin/env python3
"""
Frontend Punto de Venta - Interfaz moderna tipo POS
Servidor FastAPI optimizado para escaneo en tiempo real
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import uvicorn

# Configuración
API_BASE_URL = "http://localhost:8000/api/v1"
POS_PORT = 3002

# Crear app FastAPI
app = FastAPI(title="POS Scanner Interface", description="Interfaz tipo punto de venta para escáner")

# Configurar templates y archivos estáticos
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket manager para tiempo real
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Cliente conectado. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ Cliente desconectado. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los clientes conectados"""
        if not self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            self.active_connections.remove(conn)

# Instancia global del manager
websocket_manager = WebSocketManager()

async def check_api_connection():
    """Verificar conexión con la API backend"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"http://localhost:8000/health")
            return response.status_code == 200
    except:
        return False

async def get_productos() -> List[Dict[str, Any]]:
    """Obtener lista de productos del backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/productos/")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
    return []

async def get_producto_by_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Obtener producto específico por código"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE_URL}/productos/{codigo}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error obteniendo producto {codigo}: {e}")
    return None

async def check_usb_scanner_status() -> Dict[str, Any]:
    """Verificar estado del scanner USB"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE_URL}/usb-scanner/status")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error verificando scanner USB: {e}")
    
    return {
        "status": "error",
        "scanner_info": {"listening": False, "keyboard_library": False},
        "message": "Error de conexión con API"
    }

async def start_usb_scanner():
    """Iniciar scanner USB"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{API_BASE_URL}/usb-scanner/start")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error iniciando scanner USB: {e}")
    
    return {"status": "error", "message": "Error iniciando scanner"}

async def stop_usb_scanner():
    """Detener scanner USB"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{API_BASE_URL}/usb-scanner/stop")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error deteniendo scanner USB: {e}")
    
    return {"status": "error", "message": "Error deteniendo scanner"}

# === RUTAS WEB ===

@app.get("/", response_class=HTMLResponse)
async def pos_dashboard(request: Request):
    """Página principal - Dashboard POS"""
    api_status = await check_api_connection()
    productos = await get_productos()
    
    return templates.TemplateResponse("pos_dashboard.html", {
        "request": request,
        "api_status": api_status,
        "productos": productos[:10],  # Solo primeros 10 para el dashboard
        "total_productos": len(productos)
    })

@app.get("/pos", response_class=HTMLResponse)
async def pos_interface(request: Request):
    """Interfaz principal tipo punto de venta"""
    api_status = await check_api_connection()
    scanner_status = await check_usb_scanner_status()
    
    return templates.TemplateResponse("pos_interface.html", {
        "request": request,
        "api_status": api_status,
        "scanner_status": scanner_status
    })

@app.get("/productos", response_class=HTMLResponse)
async def pos_productos(request: Request):
    """Página de gestión de productos"""
    productos = await get_productos()
    
    return templates.TemplateResponse("pos_productos.html", {
        "request": request,
        "productos": productos
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_advanced(request: Request):
    """Dashboard ejecutivo avanzado"""
    api_status = await check_api_connection()
    
    return templates.TemplateResponse("dashboard_advanced.html", {
        "request": request,
        "api_status": api_status
    })

# === RUTAS API ===

@app.get("/api/status")
async def api_status():
    """Estado general del sistema"""
    api_conn = await check_api_connection()
    scanner_status = await check_usb_scanner_status()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "api_connected": api_conn,
        "scanner_status": scanner_status,
        "websocket_clients": len(websocket_manager.active_connections)
    }

@app.get("/api/productos")
async def api_productos():
    """Proxy para productos"""
    productos = await get_productos()
    return productos

@app.get("/api/productos/{codigo}")
async def api_producto_detalle(codigo: str):
    """Obtener producto específico"""
    producto = await get_producto_by_codigo(codigo)
    if producto:
        return producto
    return {"error": "Producto no encontrado"}, 404

@app.post("/api/scanner/start")
async def api_scanner_start():
    """Iniciar scanner USB"""
    result = await start_usb_scanner()
    
    # Notificar a todos los clientes WebSocket
    await websocket_manager.broadcast({
        "type": "scanner_started",
        "data": result,
        "timestamp": datetime.now().isoformat()
    })
    
    return result

@app.post("/api/scanner/stop")
async def api_scanner_stop():
    """Detener scanner USB"""
    result = await stop_usb_scanner()
    
    # Notificar a todos los clientes WebSocket
    await websocket_manager.broadcast({
        "type": "scanner_stopped",
        "data": result,
        "timestamp": datetime.now().isoformat()
    })
    
    return result

@app.get("/api/scanner/status")
async def api_scanner_status():
    """Estado del scanner"""
    return await check_usb_scanner_status()

# === WEBSOCKET ===

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await websocket_manager.connect(websocket)
    
    try:
        # Enviar estado inicial
        initial_status = {
            "type": "status_update",
            "data": {
                "api_connected": await check_api_connection(),
                "scanner_status": await check_usb_scanner_status(),
                "productos_count": len(await get_productos())
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(initial_status))
        
        # Mantener conexión activa y escuchar mensajes
        while True:
            try:
                # Recibir mensajes del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Procesar diferentes tipos de mensajes
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif message.get("type") == "scan_code":
                    # Simular escaneo de código
                    codigo = message.get("codigo", "")
                    if codigo:
                        producto = await get_producto_by_codigo(codigo)
                        response = {
                            "type": "scan_result",
                            "data": {
                                "codigo": codigo,
                                "producto": producto,
                                "encontrado": producto is not None
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket_manager.broadcast(response)
                
            except Exception as e:
                print(f"Error procesando mensaje WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        websocket_manager.disconnect(websocket)

# === TASK BACKGROUND ===

async def monitor_scanner():
    """Monitor del scanner para detectar escaneos automáticamente"""
    last_scan_count = 0
    
    while True:
        try:
            await asyncio.sleep(2)  # Verificar cada 2 segundos
            
            # Aquí podrías integrar lógica para detectar escaneos automáticamente
            # Por ahora, solo monitoreamos el estado
            
            scanner_status = await check_usb_scanner_status()
            if scanner_status.get("scanner_info", {}).get("listening", False):
                # Scanner está activo, continuar monitoreando
                pass
                
        except Exception as e:
            print(f"Error monitoreando scanner: {e}")
            await asyncio.sleep(5)

# === EVENTOS DE STARTUP ===

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    print("🚀 Iniciando servidor POS...")
    print(f"📱 Interfaz disponible en: http://localhost:{POS_PORT}")
    print(f"🔌 Conectando a API: {API_BASE_URL}")
    
    # Verificar conexión inicial
    api_connected = await check_api_connection()
    if api_connected:
        print("✅ Conexión con API establecida")
    else:
        print("❌ API no disponible - algunas funciones podrían no funcionar")
    
    # Iniciar monitor de scanner en background
    asyncio.create_task(monitor_scanner())

if __name__ == "__main__":
    uvicorn.run(
        "pos_server:app",
        host="0.0.0.0",
        port=POS_PORT,
        reload=True,
        log_level="info"
    )