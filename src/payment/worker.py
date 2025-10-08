#!/usr/bin/env python3
"""
Worker de Facturación Asíncrono

Este script se ejecuta como un proceso independiente para consumir mensajes de la
cola de facturación, procesarlos, interactuar con el SFE y manejar reintentos.
"""

import pika
import json
import time
import random
import sys
from pathlib import Path

# --- Añadir el directorio raíz al sys.path ---
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# ---------------------------------------------

from src.payment.dao import FacturaDAO
import streamlit as st # Para obtener la configuración de RabbitMQ

MAX_REINTENTOS = 5

class SFE_API_Simulator:
    """Simulador de una API de Sistema de Facturación Electrónica (SFE)."""
    def enviar_factura(self, datos_factura: dict) -> dict:
        """
        Simula el envío de una factura al SFE. 
        Tarda un tiempo y puede fallar aleatoriamente.
        """
        print(f"[SFE] Enviando factura ID {datos_factura.get('id')} al SFE...")
        time.sleep(random.uniform(1, 4)) # Simular latencia de red

        # 80% de probabilidad de éxito
        if random.random() < 0.8:
            print(f"[SFE] ✅ Factura ID {datos_factura.get('id')} ACEPTADA.")
            return {"status": "ok", "sfe_uuid": f"uuid-{random.randint(1000, 9999)}"}
        else:
            print(f"[SFE] ❌ Factura ID {datos_factura.get('id')} RECHAZADA.")
            return {"status": "error", "message": "Error de validación de datos (simulado)"}

def callback(ch, method, properties, body):
    """
    Función que se ejecuta por cada mensaje consumido de la cola.
    """
    print(f"\n[*] Mensaje recibido: {body.decode()}")
    mensaje = json.loads(body.decode())
    factura_id = mensaje.get("factura_id")
    intentos = mensaje.get("intentos", 0)

    factura_dao = FacturaDAO()
    sfe_simulador = SFE_API_Simulator()

    # Obtener los datos de la factura desde la BD
    # En un caso real, aquí se leerían los datos completos de la factura.
    datos_factura_simulados = {"id": factura_id, "total": 123.45}

    # Intentar enviar la factura al SFE
    resultado_sfe = sfe_simulador.enviar_factura(datos_factura_simulados)

    if resultado_sfe["status"] == "ok":
        # ÉXITO: Actualizar estado y UUID en la base de datos
        factura_dao.actualizar_estado_factura(factura_id, 'Recibida')
        # En un caso real, aquí se guardaría el UUID: factura_dao.set_sfe_uuid(factura_id, resultado_sfe["sfe_uuid"])
        print(f"[✔] Factura {factura_id} procesada y marcada como 'Recibida'.")
        ch.basic_ack(delivery_tag=method.delivery_tag) # Confirmar mensaje, se elimina de la cola
    
    else:
        # FALLO: Implementar lógica de reintento con "Exponential Backoff"
        if intentos < MAX_REINTENTOS:
            intentos += 1
            retraso = 2 ** intentos # 2, 4, 8, 16, 32 segundos
            print(f"[!] Fallo al procesar factura {factura_id}. Reintentando en {retraso}s (Intento {intentos}/{MAX_REINTENTOS}).")

            # 1. Rechazar el mensaje actual de la cola para no volver a procesarlo inmediatamente
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # 2. Esperar (esto bloquea al worker, en producción se usarían DLX de RabbitMQ)
            time.sleep(retraso)

            # 3. Publicar un NUEVO mensaje para el reintento
            nuevo_mensaje = {"factura_id": factura_id, "intentos": intentos}
            ch.basic_publish(
                exchange='',
                routing_key='facturacion',
                body=json.dumps(nuevo_mensaje),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        else:
            # Límite de reintentos alcanzado
            print(f"[🔥] Límite de reintentos para factura {factura_id} alcanzado. Marcada como 'Rechazada'.")
            factura_dao.actualizar_estado_factura(factura_id, 'Rechazada', error=resultado_sfe.get("message"))
            ch.basic_ack(delivery_tag=method.delivery_tag) # Confirmar para sacar de la cola

def main():
    print("--- Iniciando Worker de Facturación ---")
    print("Esperando mensajes de la cola 'facturacion'. Para salir, presiona CTRL+C")
    
    # Conexión a RabbitMQ
    try:
        rb_config = st.secrets.get("rabbitmq", {})
        credentials = pika.PlainCredentials(rb_config.get("username", "guest"), rb_config.get("password", "guest"))
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rb_config.get("host", "localhost"), port=rb_config.get("port", 5672), credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue='facturacion', durable=True)
        
        # Configurar el consumidor
        channel.basic_qos(prefetch_count=1) # Procesar un mensaje a la vez
        channel.basic_consume(queue='facturacion', on_message_callback=callback)
        
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ No se pudo conectar a RabbitMQ. ¿Está el servidor corriendo? - {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n--- Worker detenido manualmente ---")
        try:
            connection.close()
        except NameError:
            pass
        sys.exit(0)

if __name__ == '__main__':
    main()

