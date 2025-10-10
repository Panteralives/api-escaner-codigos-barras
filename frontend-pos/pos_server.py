#!/usr/bin/env python3
"""
Servidor TPV con Flujo de Autenticación Completo.

Este servidor FastAPI gestiona un flujo de autenticación de extremo a extremo:
- Sirve una página de login en /login.
- Protege la interfaz principal del TPV en /.
- Redirige a los usuarios no autenticados al login.
- Utiliza un sistema de tokens (access y refresh) con cookies seguras.
- Limita la tasa de intentos de login para prevenir ataques de fuerza bruta.
"""

import pika
import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

# --- Añadir el directorio raíz al sys.path ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# ----------------------------------------------

from src.payment.dao import FacturaDAO
from src.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

# --- Configuración ---
POS_PORT = 3002
COLA_FACTURACION = 'facturacion'
RABBITMQ_MAX_RETRIES = 5
RABBITMQ_RETRY_DELAY = 5

# --- Base de datos de usuarios en memoria (para demostración) ---
# Contraseña para 'testuser' es 'testpassword'.
FAKE_USERS_DB = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "$2b$12$EixZaY2V.x9.9S0zL.2L5uKx/0j6.QJ.V8L9S8.y3s9B0zL.2L5uKx",
        "disabled": False,
    }
}

# --- Rate Limiter simple en memoria ---
rate_limiter = defaultdict(list)
RATE_LIMIT_MAX_CALLS = 5
RATE_LIMIT_TIMEFRAME = timedelta(minutes=1)

# --- Inicialización de la App y Plantillas ---
app = FastAPI(
    title="POS TPV con Seguridad Completa",
    description="Servidor que gestiona la autenticación y la creación de facturas."
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# --- Middleware de Rate-Limiting ---
@app.middleware("http")
async def simple_rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    current_time = datetime.utcnow()
    rate_limiter[client_ip] = [t for t in rate_limiter[client_ip] if current_time - t < RATE_LIMIT_TIMEFRAME]
    
    if request.url.path == "/auth/token":
        if len(rate_limiter[client_ip]) >= RATE_LIMIT_MAX_CALLS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Inténtalo de nuevo más tarde."
            )
        rate_limiter[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# --- Lógica de Autenticación y Dependencias ---
def get_user_from_token(token: Optional[str]) -> Optional[dict]:
    if not token: return None
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access": return None
    username = payload.get("sub")
    return FAKE_USERS_DB.get(username)

# --- Endpoints para servir el Frontend ---

@app.get("/login", response_class=HTMLResponse)
async def serve_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def serve_pos_interface(request: Request):
    access_token = request.cookies.get("access_token")
    user = get_user_from_token(access_token)
    
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    return templates.TemplateResponse("pos_interface_v2.html", {"request": request, "user": user})

# --- Endpoints de la API de Autenticación ---

@app.post("/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    response = JSONResponse(content={"msg": "Login successful"})
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, samesite='strict',
        max_age=1800, secure=False # Set to True in production with HTTPS
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, samesite='strict',
        max_age=604800, path="/auth/token/refresh", secure=False # Set to True in production
    )
    return response


# --- API de Facturación Protegida ---

@app.post("/api/facturas", status_code=202)
async def crear_factura_y_encolar(request: Request):
    access_token = request.cookies.get("access_token")
    user = get_user_from_token(access_token)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    factura_dao = FacturaDAO()
    channel = None
    try:
        factura_id = factura_dao.crear_factura_pendiente(user_id=user['username'])
        channel = get_rabbitmq_channel()
        mensaje = {"factura_id": factura_id, "timestamp": datetime.utcnow().isoformat() + "Z"}
        
        channel.basic_publish(
            exchange='', routing_key=COLA_FACTURACION, body=json.dumps(mensaje),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        return {"status": "aceptado", "factura_id": factura_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
    finally:
        if channel and channel.is_open: channel.connection.close()


# --- Health Check y Startup --- 
@app.get("/health")
async def health_check(): return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando servidor POS...")
    for attempt in range(RABBITMQ_MAX_RETRIES):
        try:
            print(f"Verificando conexión con RabbitMQ (Intento {attempt + 1}/{RABBITMQ_MAX_RETRIES})...")
            channel = get_rabbitmq_channel()
            if channel and channel.is_open:
                print("✅ Conexión con RabbitMQ establecida.")
                channel.connection.close()
                return
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo conectar a RabbitMQ: {e}")
            if attempt < RABBITMQ_MAX_RETRIES - 1:
                print(f"Reintentando en {RABBITMQ_RETRY_DELAY} segundos...")
                time.sleep(RABBITMQ_RETRY_DELAY)
            else:
                print(f"[FATAL] La aplicación no puede iniciar sin RabbitMQ.")
                # sys.exit(1) # Comentado para no detener el entorno de desarrollo

# --- Utilidad RabbitMQ --- 
def get_rabbitmq_channel():
    """Crea y devuelve un canal de RabbitMQ, usando variables de entorno o defaults."""
    rb_host = os.getenv("RABBITMQ_HOST", "localhost")
    rb_user = os.getenv("RABBITMQ_USER", "guest")
    rb_pass = os.getenv("RABBITMQ_PASS", "guest")
    
    credentials = pika.PlainCredentials(rb_user, rb_pass)
    conn_params = pika.ConnectionParameters(host=rb_host, port=5672, credentials=credentials)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue=COLA_FACTURACION, durable=True)
    return channel
