#!/usr/bin/env python3
"""
Servidor TPV (Punto de Venta) Autónomo - Versión Simplificada

Este servidor FastAPI tiene una única responsabilidad: recibir una solicitud
para crear una factura y publicar un mensaje en la cola de RabbitMQ para
que sea procesado por el worker de facturación.

Elimina todas las dependencias de una API backend externa.
"""

import pika
import json
import sys
import time
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# --- Añadir el directorio raíz al sys.path para importaciones correctas ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# ---------------------------------------------------------------------

from src.payment.dao import FacturaDAO
import streamlit as st # Usado para obtener la configuración de secrets.toml

# --- Configuración ---
POS_PORT = 3002
COLA_FACTURACION = 'facturacion'
RABBITMQ_MAX_RETRIES = 5
RABBITMQ_RETRY_DELAY = 5 # segundos

# --- Inicialización de la App FastAPI ---
app = FastAPI(
    title="POS Invoice Trigger API",
    description="API para iniciar el proceso de facturación asíncrona."
)

# --- Utilidades de RabbitMQ ---

def get_rabbitmq_channel():
    """Crea y devuelve un canal de RabbitMQ."""
    rb_config = st.secrets.get("rabbitmq", {})
    credentials = pika.PlainCredentials(rb_config.get("username", "guest"), rb_config.get("password", "guest"))
    connection_params = pika.ConnectionParameters(
        host=rb_config.get("host", "localhost"),
        port=rb_config.get("port", 5672),
        credentials=credentials,
        connection_attempts=3,
        retry_delay=5
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=COLA_FACTURACION, durable=True)
    return channel

# --- Lógica de la API ---

@app.post("/api/facturas", status_code=202)
async def crear_factura_y_encolar(request: Request):
    """
    Endpoint principal para crear una factura.
    1. Crea un registro de factura en la BD con estado 'Pendiente'.
    2. Publica un mensaje en la cola de RabbitMQ para el procesamiento.
    Devuelve una respuesta inmediata para no bloquear al cliente.
    """
    factura_dao = FacturaDAO()
    channel = None

    try:
        # 1. Crear la factura en la base de datos
        factura_id = factura_dao.crear_factura_pendiente()
        print(f"[DB] Factura creada con ID: {factura_id}, Estado: Pendiente")

        # 2. Conectar a RabbitMQ y publicar el mensaje
        channel = get_rabbitmq_channel()
        mensaje = {
            "factura_id": factura_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "intentos": 1
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=COLA_FACTURACION,
            body=json.dumps(mensaje),
            properties=pika.BasicProperties(
                delivery_mode=2, # Hacer el mensaje persistente
            )
        )
        print(f"[RabbitMQ] Mensaje para factura ID {factura_id} publicado en la cola '{COLA_FACTURACION}'.")

        return {
            "status": "aceptado",
            "message": "La solicitud de factura ha sido aceptada y está siendo procesada.",
            "factura_id": factura_id
        }

    except Exception as e:
        print(f"[ERROR] Se produjo un error al procesar la solicitud de factura: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "No se pudo procesar la solicitud de factura en este momento."
            }
        )
    finally:
        if channel and channel.is_open:
            channel.connection.close()


@app.get("/health")
async def health_check():
    """Endpoint simple para verificar que el servidor está vivo."""
    return {"status": "ok"}

# --- Eventos de la Aplicación (con lógica de reintentos) ---

@app.on_event("startup")
async def startup_event():
    """Verifica la conexión a RabbitMQ al iniciar con reintentos."""
    print("🚀 Iniciando servidor POS...")
    
    for attempt in range(RABBITMQ_MAX_RETRIES):
        try:
            print(f"Verificando conexión con RabbitMQ (Intento {attempt + 1}/{RABBITMQ_MAX_RETRIES})...")
            channel = get_rabbitmq_channel()
            if channel and channel.is_open:
                print("✅ Conexión con RabbitMQ establecida y cola verificada.")
                channel.connection.close()
                print(f"📱 Servidor listo. Escuchando en http://localhost:{POS_PORT}")
                return # Salir de la función si la conexión es exitosa
            else:
                raise ConnectionError("El canal de RabbitMQ no se pudo abrir.")
        except (pika.exceptions.AMQPConnectionError, ConnectionError) as e:
            print(f"[ADVERTENCIA] No se pudo conectar a RabbitMQ: {e}")
            if attempt < RABBITMQ_MAX_RETRIES - 1:
                print(f"Reintentando en {RABBITMQ_RETRY_DELAY} segundos...")
                time.sleep(RABBITMQ_RETRY_DELAY)
            else:
                print(f"[FATAL] La aplicación no puede iniciar sin RabbitMQ después de {RABBITMQ_MAX_RETRIES} intentos.")
                sys.exit(1) # Detener la aplicación si todos los reintentos fallan

