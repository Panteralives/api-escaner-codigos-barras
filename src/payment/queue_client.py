#!/usr/bin/env python3
"""
Cliente para interactuar con una cola de mensajes RabbitMQ.

Utiliza la librería `pika` para la comunicación.
"""

import pika
import json
import streamlit as st # Usado para el manejo de secretos/configuración

class QueueClient:
    """
    Gestiona la conexión y publicación de mensajes en RabbitMQ.
    """

    def __init__(self):
        """
        Establece la conexión con RabbitMQ usando credenciales de la configuración.
        """
        self.connection = None
        self.channel = None
        try:
            # Obtener configuración de RabbitMQ desde los secretos 
            # (análogo a un vault)
            # Se debe configurar en .streamlit/secrets.toml
            # [rabbitmq]
            # host = "localhost"
            # port = 5672
            # username = "guest"
            # password = "guest"
            rb_config = st.secrets.get("rabbitmq", {})
            host = rb_config.get("host", "localhost")
            port = rb_config.get("port", 5672)
            
            credentials = pika.PlainCredentials(
                rb_config.get("username", "guest"), 
                rb_config.get("password", "guest")
            )
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, port=port, credentials=credentials)
            )
            self.channel = self.connection.channel()
            print("✅ Conexión con RabbitMQ establecida.")

        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Error de conexión con RabbitMQ: {e}")
            # El sistema debe poder funcionar incluso si RabbitMQ está caído.
            # Los errores serán manejados en el Facade.
            self.connection = None
            self.channel = None

    def publicar_mensaje(self, nombre_cola: str, mensaje: dict):
        """
        Publica un mensaje en una cola específica.

        Args:
            nombre_cola: El nombre de la cola (ej. 'facturacion').
            mensaje: Un diccionario que será convertido a JSON.
        """
        if not self.channel or not self.channel.is_open:
            print("⚠️ No se puede publicar: No hay conexión con RabbitMQ.")
            raise ConnectionError("No hay conexión con el servidor de colas.")

        try:
            # Declarar la cola (es idempotente, solo la crea si no existe)
            # durable=True asegura que la cola sobreviva a reinicios del broker
            self.channel.queue_declare(queue=nombre_cola, durable=True)

            # Publicar el mensaje
            # delivery_mode=2 hace el mensaje persistente
            self.channel.basic_publish(
                exchange='',
                routing_key=nombre_cola,
                body=json.dumps(mensaje),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Hacer mensaje persistente
                )
            )
            print(f"[>] Mensaje publicado en la cola '{nombre_cola}': {mensaje}")
        except Exception as e:
            print(f"❌ Error publicando mensaje en RabbitMQ: {e}")
            raise

    def close_connection(self):
        """Cierra la conexión con RabbitMQ si está abierta."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("🔒 Conexión con RabbitMQ cerrada.")

    def __del__(self):
        """Destructor para asegurar que la conexión se cierre."""
        self.close_connection()

