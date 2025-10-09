#!/usr/bin/env python3
"""
Worker de Facturación Asíncrono - Versión Mejorada

Este worker consume mensajes de RabbitMQ y procesa cada uno de forma robusta.
- Simula una API SFE con diferentes tipos de errores (permanentes y transitorios).
- Utiliza logging con timestamps para una mejor trazabilidad.
- Implementa una lógica de reintento inteligente que solo reintenta en fallos transitorios.
"""

import pika
import json
import time
import random
import sys
from pathlib import Path
from datetime import datetime

# --- Añadir el directorio raíz al sys.path para importaciones correctas ---
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# ---------------------------------------------------------------------

from src.payment.dao import FacturaDAO
import streamlit as st # Usado para obtener la configuración de secrets.toml

# --- Constantes y Configuración ---
MAX_REINTENTOS = 4
COLA_FACTURACION = 'facturacion'

# --- Utilidad de Logging ---
def log(mensaje: str):
    """Imprime un mensaje con un timestamp UTC."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}Z] {mensaje}")

# --- Simulador de API Externa (SFE) ---
class SFE_API_Simulator:
    """
    Simulador mejorado de una API de Sistema de Facturación Electrónica (SFE).
    Ahora simula respuestas similares a HTTP con diferentes probabilidades.
    """
    def enviar_factura(self, datos_factura: dict) -> dict:
        """
        Simula el envío de una factura al SFE.
        - 70% de éxito (200 OK)
        - 15% de error de cliente (400 Bad Request) -> No se debe reintentar.
        - 15% de error de servidor (503 Service Unavailable) -> Se debe reintentar.
        """
        factura_id = datos_factura.get('id')
        log(f"[SFE] Enviando factura ID {factura_id}...")
        time.sleep(random.uniform(0.5, 2.5)) # Simular latencia de red

        rand_val = random.random()
        
        if rand_val < 0.70: # Éxito
            log(f"[SFE] ✅ Factura ID {factura_id} ACEPTADA.")
            return {
                "status_code": 200,
                "body": {"status": "ok", "sfe_uuid": f"uuid-{random.randint(1000, 9999)}"}
            }
        elif rand_val < 0.85: # Error de Cliente (permanente)
            log(f"[SFE] ❌ Factura ID {factura_id} RECHAZADA (Datos inválidos).")
            return {
                "status_code": 400,
                "body": {"status": "error", "message": "Error 400: Datos de la factura no válidos (simulado)."}
            }
        else: # Error de Servidor (transitorio)
            log(f"[SFE] ❌ Factura ID {factura_id} FALLÓ (Servidor no disponible).")
            return {
                "status_code": 503,
                "body": {"status": "error", "message": "Error 503: El servicio SFE no está disponible temporalmente (simulado)."}
            }

# --- Lógica del Consumidor de RabbitMQ ---
class Worker:
    def __init__(self):
        self.factura_dao = FacturaDAO()
        self.sfe_simulador = SFE_API_Simulator()
        self.connection = None
        self.channel = None

    def _conectar_rabbitmq(self):
        """Establece la conexión y el canal con RabbitMQ."""
        rb_config = st.secrets.get("rabbitmq", {})
        credentials = pika.PlainCredentials(rb_config.get("username", "guest"), rb_config.get("password", "guest"))
        params = pika.ConnectionParameters(
            host=rb_config.get("host", "localhost"),
            port=rb_config.get("port", 5672),
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=COLA_FACTURACION, durable=True)
        self.channel.basic_qos(prefetch_count=1) # Procesar un mensaje a la vez
        log("[RabbitMQ] Conexión establecida y cola declarada.")

    def _procesar_mensaje(self, ch, method, properties, body):
        """Punto central de la lógica de procesamiento para cada mensaje."""
        try:
            mensaje = json.loads(body.decode())
            factura_id = mensaje.get("factura_id")
            intentos = mensaje.get("intentos", 1)
            log(f"[*] Mensaje recibido para factura ID {factura_id} (Intento #{intentos}).")
            
            # 1. Simular envío al SFE
            datos_factura = {"id": factura_id} # Simulación, en un caso real se carga desde la DB
            resultado_sfe = self.sfe_simulador.enviar_factura(datos_factura)
            
            # 2. Interpretar la respuesta del SFE
            status_code = resultado_sfe["status_code"]

            if status_code == 200:
                # ÉXITO FINAL
                self.factura_dao.actualizar_estado_factura(factura_id, 'Recibida')
                log(f"[✔] Factura {factura_id} procesada exitosamente y marcada como 'Recibida'.")
                ch.basic_ack(delivery_tag=method.delivery_tag)

            elif 400 <= status_code < 500:
                # ERROR PERMANENTE (No reintentar)
                error_msg = resultado_sfe["body"].get("message", "Error desconocido del cliente.")
                self.factura_dao.actualizar_estado_factura(factura_id, 'Rechazada', error=error_msg)
                log(f"[🔥] Error permanente para factura {factura_id}. Marcada como 'Rechazada'. Motivo: {error_msg}")
                ch.basic_ack(delivery_tag=method.delivery_tag) # Sacar de la cola

            else: # ERROR TRANSITORIO (5xx)
                # Reintentar si no hemos superado el límite
                if intentos < MAX_REINTENTOS:
                    self._republicar_para_reintento(ch, method, factura_id, intentos)
                else:
                    error_msg = f"Se superó el límite de {MAX_REINTENTOS} reintentos."
                    self.factura_dao.actualizar_estado_factura(factura_id, 'Rechazada', error=error_msg)
                    log(f"[🔥] Límite de reintentos para factura {factura_id} alcanzado. Marcada como 'Rechazada'.")
                    ch.basic_ack(delivery_tag=method.delivery_tag) # Sacar de la cola
        
        except json.JSONDecodeError:
            log("[!] Error: Mensaje no es un JSON válido. Descartando.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            log(f"[!] Se produjo un error inesperado en el procesamiento: {e}. El mensaje será rechazado.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Evitar bucles de envenenamiento

    def _republicar_para_reintento(self, ch, method, factura_id: int, intentos_actuales: int):
        """Nacks el mensaje actual y publica uno nuevo para un reintento futuro."""
        # Rechazar el mensaje actual para que no vuelva a la cola inmediatamente
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        retraso = 2 ** intentos_actuales # Exponential backoff: 2, 4, 8, 16s
        log(f"[!] Fallo transitorio en factura {factura_id}. Reintentando en {retraso}s (Intento {intentos_actuales+1}/{MAX_REINTENTOS}).")
        
        # Bloquear la ejecución (simple para este ejemplo, en producción usar DLX de RabbitMQ)
        time.sleep(retraso)

        # Publicar un nuevo mensaje con el contador de intentos incrementado
        nuevo_mensaje = {"factura_id": factura_id, "intentos": intentos_actuales + 1}
        ch.basic_publish(
            exchange='',
            routing_key=COLA_FACTURACION,
            body=json.dumps(nuevo_mensaje),
            properties=pika.BasicProperties(delivery_mode=2) # Mensaje persistente
        )
        log(f"[*] Mensaje para reintento de factura {factura_id} publicado.")

    def start(self):
        """Inicia la conexión y el consumo de mensajes."""
        log("--- Iniciando Worker de Facturación ---")
        try:
            self._conectar_rabbitmq()
            self.channel.basic_consume(queue=COLA_FACTURACION, on_message_callback=self._procesar_mensaje)
            log("Esperando mensajes. Para salir, presiona CTRL+C")
            self.channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            log(f"❌ No se pudo conectar a RabbitMQ. ¿Está el servidor corriendo? - {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            log("\n--- Worker detenido manualmente ---")
            if self.connection and self.connection.is_open:
                self.connection.close()
            sys.exit(0)

def main():
    worker = Worker()
    worker.start()

if __name__ == '__main__':
    main()
