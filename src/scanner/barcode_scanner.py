import cv2
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple
import logging
import io

# Deshabilitar pyzbar temporalmente por problemas en Windows
PYZBAR_AVAILABLE = False
print("⚠️ pyzbar deshabilitado - usando solo scanner USB-HID")
print("💡 Para habilitar cámara, soluciona las dependencias de pyzbar en Windows")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BarcodeScanner:
    """Clase para escanear códigos de barras usando OpenCV y pyzbar"""
    
    def __init__(self, camera_index: int = 0):
        """
        Inicializar el escáner
        
        Args:
            camera_index: Índice de la cámara (normalmente 0 para cámara principal)
        """
        self.camera_index = camera_index
        self.cap = None
        
    def start_camera(self) -> bool:
        """
        Inicializar la cámara
        
        Returns:
            True si la cámara se inicializó correctamente, False en caso contrario
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"No se pudo abrir la cámara con índice {self.camera_index}")
                return False
            
            # Configurar resolución (opcional)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            logger.info(f"Cámara inicializada correctamente (índice: {self.camera_index})")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar cámara: {e}")
            return False
    
    def stop_camera(self):
        """Detener la cámara y liberar recursos"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            logger.info("Cámara detenida")
    
    def scan_from_camera(self) -> Optional[Tuple[str, str]]:
        """
        Escanear código desde cámara en tiempo real
        
        Returns:
            Tupla (código, tipo) si se encuentra código, None en caso contrario
        """
        if not PYZBAR_AVAILABLE:
            logger.error("pyzbar no disponible - usa el scanner USB-HID en su lugar")
            return None
            
        if self.cap is None or not self.cap.isOpened():
            logger.error("Cámara no inicializada")
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("No se pudo capturar frame de la cámara")
                return None
            
            # Convertir frame a formato para pyzbar
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Importar pyzbar solo cuando sea necesario
            try:
                from pyzbar import pyzbar
                # Escanear códigos de barras
                barcodes = pyzbar.decode(gray)
            except Exception as e:
                logger.error(f"Error importando pyzbar: {e}")
                return None
            
            if barcodes:
                for barcode in barcodes:
                    # Obtener datos del código
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    logger.info(f"Código escaneado: {barcode_data} (tipo: {barcode_type})")
                    return barcode_data, barcode_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error al escanear desde cámara: {e}")
            return None
    
    def scan_from_image_bytes(self, image_bytes: bytes) -> Optional[Tuple[str, str]]:
        """
        Escanear código desde imagen en bytes
        
        Args:
            image_bytes: Imagen en formato bytes
            
        Returns:
            Tupla (código, tipo) si se encuentra código, None en caso contrario
        """
        if not PYZBAR_AVAILABLE:
            logger.error("pyzbar no disponible - usa el scanner USB-HID en su lugar")
            return None
            
        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir PIL a numpy array
            image_np = np.array(image)
            
            # Convertir a escala de grises si es necesario
            if len(image_np.shape) == 3:
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_np
            
            # Importar pyzbar solo cuando sea necesario
            try:
                from pyzbar import pyzbar
                # Escanear códigos de barras
                barcodes = pyzbar.decode(gray)
            except Exception as e:
                logger.error(f"Error importando pyzbar: {e}")
                return None
            
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    logger.info(f"Código escaneado desde imagen: {barcode_data} (tipo: {barcode_type})")
                    return barcode_data, barcode_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error al escanear desde imagen: {e}")
            return None
    
    def scan_from_file(self, image_path: str) -> Optional[Tuple[str, str]]:
        """
        Escanear código desde archivo de imagen
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            Tupla (código, tipo) si se encuentra código, None en caso contrario
        """
        if not PYZBAR_AVAILABLE:
            logger.error("pyzbar no disponible - usa el scanner USB-HID en su lugar")
            return None
            
        try:
            # Leer imagen
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"No se pudo cargar la imagen: {image_path}")
                return None
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Importar pyzbar solo cuando sea necesario
            try:
                from pyzbar import pyzbar
                # Escanear códigos de barras
                barcodes = pyzbar.decode(gray)
            except Exception as e:
                logger.error(f"Error importando pyzbar: {e}")
                return None
            
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    logger.info(f"Código escaneado desde archivo: {barcode_data} (tipo: {barcode_type})")
                    return barcode_data, barcode_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error al escanear desde archivo: {e}")
            return None
    
    def get_camera_frame(self) -> Optional[np.ndarray]:
        """
        Obtener frame actual de la cámara para mostrar en frontend
        
        Returns:
            Frame como numpy array o None si hay error
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
            return None
        except Exception as e:
            logger.error(f"Error al obtener frame: {e}")
            return None
    
    @staticmethod
    def is_camera_available(camera_index: int = 0) -> bool:
        """
        Verificar si una cámara está disponible
        
        Args:
            camera_index: Índice de la cámara a verificar
            
        Returns:
            True si la cámara está disponible, False en caso contrario
        """
        try:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                return ret
            return False
        except Exception:
            return False