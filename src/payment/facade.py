
from .dao import FacturaDAO
from .queue_client import QueueClient

class SFEFacade:
    """
    Proporciona una interfaz simplificada (Facade) para interactuar con el 
    Sistema de Facturación Electrónica (SFE).
    
    Abstrae la complejidad de la comunicación asíncrona, reintentos y 
    almacenamiento local.
    """

    def __init__(self):
        """
        Inicializa el DAO para la base de datos y el cliente de la cola de mensajes.
        """
        self.factura_dao = FacturaDAO()
        self.queue_client = QueueClient()

    def crear_factura(self, datos_venta: dict) -> dict:
        """
        Punto de entrada principal para iniciar el proceso de facturación.

        1. Valida los datos de entrada.
        2. Almacena una representación inicial de la factura en la DB local 
           con estado 'No Enviada'.
        3. Publica un mensaje en la cola para el procesamiento asíncrono.
        4. Devuelve una respuesta inmediata al TPV (Punto de Venta).

        Args:
            datos_venta: Un diccionario con la información de la venta.

        Returns:
            Un diccionario con el ID de la factura local y un mensaje de estado.
        """
        # 1. Validación de datos de entrada
        if not self._validar_datos(datos_venta):
            return {"status": "error", "message": "Datos de venta inválidos"}

        # 2. Almacenamiento local inicial
        factura_id = self.factura_dao.crear_factura_inicial(datos_venta)
        if not factura_id:
            return {"status": "error", "message": "No se pudo crear el registro de la factura en la base de datos."}

        # 3. Publicar en la cola de mensajes
        try:
            mensaje_cola = {"factura_id": factura_id, "intentos": 0}
            self.queue_client.publicar_mensaje('facturacion', mensaje_cola)
            
            # Actualizar el estado local a 'En Cola'
            self.factura_dao.actualizar_estado_factura(factura_id, 'En Cola')
            
        except ConnectionError as e:
            # ----- MECANISMO DE CONTINGENCIA (FALLBACK) -----
            # Si RabbitMQ está caído, no podemos ponerlo 'En Cola'.
            # El estado permanece como 'No Enviada'. Un worker de 
            # recuperación podría procesarlo más tarde.
            print(f"⚠️ Fallback: RabbitMQ no disponible. La factura {factura_id} queda como 'No Enviada'.")
            # No es necesario hacer nada más aquí, la factura ya está en 'No Enviada'.
            pass # La respuesta al TPV será la misma.

        # 4. Respuesta inmediata al TPV
        return {
            "status": "procesando",
            "message": "La factura ha sido recibida y está siendo procesada.",
            "factura_id_local": factura_id
        }

    def consultar_estado_factura(self, factura_id: int) -> dict:
        """
        Consulta el estado de una factura en la base de datos local.
        """
        estado = self.factura_dao.get_estado_factura(factura_id)
        if estado:
            return {"factura_id": factura_id, "estado": estado}
        return {"status": "error", "message": "Factura no encontrada"}

    def _validar_datos(self, datos_venta: dict) -> bool:
        """Placeholder para la lógica de validación de datos de la venta."""
        if "productos" in datos_venta and "metodo_pago" in datos_venta:
            return True
        return False

    def __del__(self):
        """
Asegura que la conexión de la cola se cierre limpiamente.
        """
        if self.queue_client:
            self.queue_client.close_connection()
