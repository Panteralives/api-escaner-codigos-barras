#!/usr/bin/env python3
"""
Módulo para Scanner de Código de Barras USB-HID
==============================================

Este módulo maneja lectores de código de barras que se conectan por USB
y funcionan como dispositivos HID (Human Interface Device), simulando
un teclado que "escribe" el código escaneado.

Funcionalidades:
- Captura global de entrada de teclado
- Detección automática de códigos de barras
- Filtrado de entradas para separar scanner de teclado real
- Callbacks para procesar códigos escaneados
- Configuración de caracteres terminadores
"""

import time
import threading
import queue
import logging
import os
from typing import Optional, Callable, List
from dotenv import load_dotenv

# Importar biblioteca para captura de teclado
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️ Advertencia: biblioteca 'keyboard' no instalada")
    print("💡 Instala con: pip install keyboard")

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


class USBHIDScanner:
    """
    Clase para manejar lectores de código de barras USB-HID
    
    Características:
    - Captura global de entradas de teclado
    - Diferencia entre scanner y teclado normal por velocidad
    - Detección automática de códigos por caracteres terminadores
    - Callbacks asíncronos para procesar códigos
    - Buffer configurable para acumular caracteres
    """
    
    def __init__(self):
        # Configuración desde variables de entorno (más estricta para evitar captura de teclado)
        self.min_barcode_length = int(os.getenv('MIN_BARCODE_LENGTH', '8'))  # Mínimo 8 caracteres
        self.max_barcode_length = int(os.getenv('MAX_BARCODE_LENGTH', '50'))
        self.scanner_speed_threshold = float(os.getenv('SCANNER_SPEED_MS', '150'))  # Más rápido para scanners reales
        
        # Caracteres terminadores comunes en scanners
        self.terminator_chars = [
            'enter',      # Enter
            'tab',        # Tab
            'space',      # Espacio (algunos scanners)
        ]
        
        # Estado interno
        self.is_listening = False
        self.listening_thread: Optional[threading.Thread] = None
        self.callback_function: Optional[Callable] = None
        
        # Buffer para acumular caracteres
        self.current_barcode = ""
        self.last_key_time = 0
        self.key_times: List[float] = []
        
        logger.info("Inicializando Scanner USB-HID")
        
        if not KEYBOARD_AVAILABLE:
            logger.error("❌ Biblioteca 'keyboard' no disponible")

    def _is_scanner_input(self, char_times: List[float]) -> bool:
        """
        Determina si la entrada viene del scanner basándose en la velocidad
        Los scanners escriben muy rápido y consistente
        
        Args:
            char_times: Lista de tiempos entre caracteres
            
        Returns:
            True si parece entrada de scanner, False si es teclado manual
        """
        if len(char_times) < 2:
            return False
        
        # Calcular tiempo promedio entre caracteres
        avg_time = sum(char_times) / len(char_times)
        
        # Los scanners son muy consistentes en velocidad
        time_variance = sum(abs(t - avg_time) for t in char_times) / len(char_times)
        
        # Criterios para detectar scanner (ajustados para evitar teclado manual):
        # 1. Velocidad promedio rápida (< 150ms entre caracteres)
        # 2. Variación baja en la velocidad (muy consistente)
        is_fast = avg_time < self.scanner_speed_threshold
        is_consistent = time_variance < 80  # ms (más estricto)
        
        logger.debug(f"Análisis de entrada - Promedio: {avg_time:.1f}ms, Variación: {time_variance:.1f}ms")
        
        return is_fast and is_consistent

    def _on_key_event(self, event):
        """
        Callback que se ejecuta con cada evento de teclado
        
        Args:
            event: Evento de teclado capturado
        """
        try:
            # Solo procesar eventos de teclas presionadas (no liberadas)
            if event.event_type != keyboard.KEY_DOWN:
                return
            
            current_time = time.time() * 1000  # Convertir a milisegundos
            
            # Verificar si es un carácter terminador
            if event.name in self.terminator_chars:
                self._process_potential_barcode()
                return
            
            # Solo procesar caracteres alfanuméricos y símbolos comunes
            if len(event.name) == 1 and event.name.isprintable():
                # Calcular tiempo desde último carácter
                if self.last_key_time > 0:
                    time_diff = current_time - self.last_key_time
                    self.key_times.append(time_diff)
                
                # Agregar carácter al buffer
                self.current_barcode += event.name
                self.last_key_time = current_time
                
                logger.debug(f"Carácter capturado: '{event.name}' - Buffer: '{self.current_barcode}'")
                
                # Limpiar buffer si es muy largo (probablemente no es código de barras)
                if len(self.current_barcode) > self.max_barcode_length:
                    self._reset_buffer()
            
            # Resetear buffer si pasa mucho tiempo sin actividad
            elif current_time - self.last_key_time > 1000:  # 1 segundo de inactividad
                self._reset_buffer()
                
        except Exception as e:
            logger.error(f"❌ Error procesando evento de teclado: {e}")

    def _process_potential_barcode(self):
        """
        Procesa un posible código de barras cuando se detecta un terminador
        """
        try:
            if not self.current_barcode:
                return
            
            # Verificar longitud mínima
            if len(self.current_barcode) < self.min_barcode_length:
                logger.debug(f"Código muy corto ignorado: '{self.current_barcode}'")
                self._reset_buffer()
                return
            
            # Verificar que sea principalmente numérico (códigos de barras típicos)
            numeric_chars = sum(1 for c in self.current_barcode if c.isdigit())
            if numeric_chars < len(self.current_barcode) * 0.7:  # Al menos 70% números
                logger.debug(f"Código con pocas cifras ignorado: '{self.current_barcode}' ({numeric_chars}/{len(self.current_barcode)} números)")
                self._reset_buffer()
                return
            
            # Verificar si parece entrada de scanner basándose en velocidad
            if len(self.key_times) > 1 and self._is_scanner_input(self.key_times):
                barcode = self.current_barcode.strip()
                logger.info(f"📷 Código de barras detectado: '{barcode}'")
                
                # Llamar callback si está configurado
                if self.callback_function:
                    # Ejecutar callback en hilo separado para no bloquear
                    threading.Thread(
                        target=self.callback_function,
                        args=(barcode,),
                        daemon=True
                    ).start()
                
            else:
                logger.debug(f"Entrada de teclado manual ignorada: '{self.current_barcode}'")
            
        except Exception as e:
            logger.error(f"❌ Error procesando código de barras: {e}")
        finally:
            self._reset_buffer()

    def _reset_buffer(self):
        """
        Resetea el buffer de caracteres y tiempos
        """
        self.current_barcode = ""
        self.key_times.clear()
        self.last_key_time = 0

    def set_barcode_callback(self, callback_function: Callable):
        """
        Establece la función que se llamará cuando se escanee un código de barras
        
        Args:
            callback_function: Función que recibe el código escaneado como parámetro
        """
        self.callback_function = callback_function
        logger.info("✅ Función callback configurada para scanner HID")

    def start_listening(self) -> bool:
        """
        Inicia la escucha global de eventos de teclado
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if not KEYBOARD_AVAILABLE:
            logger.error("❌ No se puede iniciar: biblioteca 'keyboard' no disponible")
            return False
        
        if self.is_listening:
            logger.warning("⚠️ Ya está escuchando eventos de teclado")
            return True
        
        try:
            logger.info("🎧 Iniciando escucha global de teclado para scanner...")
            
            # Configurar hook global para capturar todas las teclas
            keyboard.hook(self._on_key_event)
            
            self.is_listening = True
            logger.info("✅ Escucha de scanner HID iniciada correctamente")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando escucha de teclado: {e}")
            return False

    def stop_listening(self):
        """
        Detiene la escucha de eventos de teclado
        """
        if not self.is_listening:
            return
        
        try:
            keyboard.unhook_all()
            self.is_listening = False
            self._reset_buffer()
            logger.info("✅ Escucha de scanner HID detenida")
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo escucha: {e}")

    def test_scanner(self, timeout_seconds: int = 30) -> Optional[str]:
        """
        Función de prueba para verificar que el scanner funciona
        
        Args:
            timeout_seconds: Tiempo máximo a esperar por un código
            
        Returns:
            Código escaneado o None si no se detectó ninguno
        """
        logger.info(f"🧪 Iniciando prueba de scanner (timeout: {timeout_seconds}s)...")
        logger.info("📷 Por favor, escanea un código de barras...")
        
        # Cola para recibir el código desde el callback
        test_queue = queue.Queue()
        
        def test_callback(barcode):
            test_queue.put(barcode)
        
        # Configurar callback temporal
        original_callback = self.callback_function
        self.set_barcode_callback(test_callback)
        
        # Iniciar escucha si no está activa
        was_listening = self.is_listening
        if not was_listening:
            if not self.start_listening():
                return None
        
        try:
            # Esperar por un código
            barcode = test_queue.get(timeout=timeout_seconds)
            logger.info(f"✅ Código detectado en prueba: '{barcode}'")
            return barcode
            
        except queue.Empty:
            logger.warning("⏰ Timeout: No se detectó ningún código de barras")
            return None
            
        finally:
            # Restaurar estado original
            self.callback_function = original_callback
            if not was_listening:
                self.stop_listening()

    def get_status(self) -> dict:
        """
        Obtiene el estado actual del scanner HID
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'type': 'USB-HID',
            'listening': self.is_listening,
            'keyboard_library': KEYBOARD_AVAILABLE,
            'min_barcode_length': self.min_barcode_length,
            'max_barcode_length': self.max_barcode_length,
            'speed_threshold_ms': self.scanner_speed_threshold,
            'current_buffer': self.current_barcode,
            'buffer_length': len(self.current_barcode)
        }


# Función de conveniencia para crear instancia global
_hid_scanner_instance = None

def get_hid_scanner() -> USBHIDScanner:
    """
    Función para obtener una instancia global del scanner HID
    
    Returns:
        Instancia única de USBHIDScanner
    """
    global _hid_scanner_instance
    
    if _hid_scanner_instance is None:
        _hid_scanner_instance = USBHIDScanner()
    
    return _hid_scanner_instance


# Ejemplo de uso
if __name__ == "__main__":
    """
    Script de prueba para verificar el funcionamiento del scanner HID
    """
    
    # Configurar logging para ver los mensajes
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Crear instancia del scanner
    scanner = USBHIDScanner()
    
    # Función que se ejecuta cuando se escanea un código
    def on_barcode_scanned(barcode):
        print(f"\n🎯 ¡CÓDIGO ESCANEADO!: '{barcode}'")
        print(f"📏 Longitud: {len(barcode)} caracteres")
        print("-" * 50)
    
    # Configurar callback
    scanner.set_barcode_callback(on_barcode_scanned)
    
    # Mostrar estado
    status = scanner.get_status()
    print(f"\n📊 Estado del scanner HID: {status}")
    
    if not KEYBOARD_AVAILABLE:
        print("\n❌ No se puede continuar sin la biblioteca 'keyboard'")
        print("📦 Instala con: pip install keyboard")
        exit(1)
    
    print("\n🎧 Iniciando escucha de scanner USB-HID...")
    print("📷 Escanea códigos de barras - Se detectarán automáticamente")
    print("⏹️  Presiona Ctrl+C para salir")
    print("-" * 50)
    
    # Iniciar escucha
    if scanner.start_listening():
        try:
            # Mantener el programa ejecutándose
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo scanner...")
            scanner.stop_listening()
            print("👋 ¡Adiós!")
    else:
        print("\n❌ No se pudo iniciar el scanner HID")