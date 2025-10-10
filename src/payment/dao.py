
import sqlite3

# Asumiremos una base de datos SQLite para simplicidad.
# En un entorno real, esto podría ser PostgreSQL, MySQL, etc.
DB_PATH = "./facturacion.db"

class FacturaDAO:
    """
    Data Access Object (DAO) para gestionar la persistencia de las facturas
    en la base de datos local.
    """

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        """Crea la tabla de facturas si no existe."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datos_venta TEXT NOT NULL,
                estado TEXT NOT NULL CHECK(estado IN (
                    'No Enviada', 
                    'En Cola', 
                    'Enviada', 
                    'Recibida', 
                    'Rechazada', 
                    'Contingencia'
                )),
                sfe_uuid TEXT,
                intentos INTEGER DEFAULT 0,
                ultimo_error TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def crear_factura_inicial(self, datos_venta: dict) -> int:
        """
        Crea un registro inicial para una factura con estado 'No Enviada'.
        Devuelve el ID de la factura creada.
        """
        import json
        cursor = self.conn.cursor()
        sql = "INSERT INTO facturas (datos_venta, estado) VALUES (?, ?)"
        
        # Convertir el diccionario de datos de venta a un string JSON
        datos_venta_json = json.dumps(datos_venta)
        
        cursor.execute(sql, (datos_venta_json, 'No Enviada'))
        self.conn.commit()
        return cursor.lastrowid

    def actualizar_estado_factura(self, factura_id: int, nuevo_estado: str, error: str = None):
        """
        Actualiza el estado de una factura y opcionalmente un mensaje de error.
        """
        cursor = self.conn.cursor()
        sql = "UPDATE facturas SET estado = ?, ultimo_error = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(sql, (nuevo_estado, error, factura_id))
        self.conn.commit()

    def incrementar_intentos(self, factura_id: int):
        """
        Incrementa el contador de reintentos para una factura.
        """
        cursor = self.conn.cursor()
        sql = "UPDATE facturas SET intentos = intentos + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(sql, (factura_id,))
        self.conn.commit()

    def get_estado_factura(self, factura_id: int) -> str:
        """Obtiene el estado actual de una factura."""
        cursor = self.conn.cursor()
        sql = "SELECT estado FROM facturas WHERE id = ?"
        cursor.execute(sql, (factura_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

    def __del__(self):
        """Cierra la conexión a la base de datos al destruir el objeto."""
        if self.conn:
            self.conn.close()
