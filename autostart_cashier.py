#!/usr/bin/env python3
"""
🛒 SISTEMA POS - AUTOINICIO CAJERO
================================

Script optimizado específicamente para iniciar el frontend del cajero
automáticamente en Windows.

Autor: Claude AI Assistant
Fecha: 01 de Octubre, 2025
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import logging
from pathlib import Path
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autostart_cashier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CashierAutoStart:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.api_port = 8000
        self.frontend_port = 3002
        self.api_url = f"http://localhost:{self.api_port}"
        self.frontend_url = f"http://localhost:{self.frontend_port}"
        
        self.api_process = None
        self.frontend_process = None
    
    def start_backend_api(self):
        """Iniciar el backend API usando run.py"""
        logger.info("Iniciando backend API...")
        
        try:
            # Usar run.py que sabemos que funciona
            self.api_process = subprocess.Popen(
                [sys.executable, "run.py"],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Ocultar ventana
            )
            
            logger.info(f"Backend API iniciado con PID: {self.api_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando backend API: {e}")
            return False
    
    def start_cashier_frontend(self):
        """Iniciar el frontend del cajero (POS)"""
        logger.info("Iniciando frontend del cajero...")
        
        try:
            # Buscar el archivo del frontend POS
            pos_server = self.project_dir / "frontend-pos" / "pos_server.py"
            
            if pos_server.exists():
                self.frontend_process = subprocess.Popen(
                    [sys.executable, str(pos_server)],
                    cwd=pos_server.parent,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW  # Ocultar ventana
                )
                logger.info(f"Frontend POS iniciado con PID: {self.frontend_process.pid}")
                return True
            else:
                logger.warning(f"Archivo pos_server.py no encontrado en {pos_server}")
                return False
                
        except Exception as e:
            logger.error(f"Error iniciando frontend del cajero: {e}")
            return False
    
    def wait_and_open_browser(self, delay=15):
        """Esperar y abrir el navegador con la interfaz del cajero"""
        def open_browser():
            logger.info(f"Esperando {delay} segundos para que los servicios inicien...")
            time.sleep(delay)
            
            # Intentar abrir la interfaz del cajero primero
            try:
                logger.info(f"Abriendo interfaz del cajero en {self.frontend_url}")
                webbrowser.open(self.frontend_url)
            except Exception as e:
                logger.error(f"Error abriendo interfaz del cajero: {e}")
                # Fallback: abrir la documentación de la API
                try:
                    logger.info(f"Fallback: Abriendo documentación API en {self.api_url}/docs")
                    webbrowser.open(f"{self.api_url}/docs")
                except Exception as e2:
                    logger.error(f"Error abriendo documentación API: {e2}")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=open_browser, daemon=True)
        thread.start()
    
    def cleanup(self):
        """Limpiar procesos al cerrar"""
        logger.info("Cerrando procesos del sistema POS...")
        
        for process_name, process in [("Backend API", self.api_process), ("Frontend", self.frontend_process)]:
            if process and process.poll() is None:
                logger.info(f"Terminando {process_name} (PID: {process.pid})")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Forzando cierre de {process_name}")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error cerrando {process_name}: {e}")
    
    def run(self):
        """Ejecutar inicio automático del sistema cajero"""
        logger.info("=" * 50)
        logger.info("SISTEMA POS - AUTOINICIO CAJERO")
        logger.info("=" * 50)
        logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. Iniciar backend API
            if not self.start_backend_api():
                logger.error("No se pudo iniciar el backend API")
                return False
            
            # 2. Esperar un poco para que el API inicie
            logger.info("Esperando a que el backend API inicie...")
            time.sleep(8)
            
            # 3. Iniciar frontend del cajero
            frontend_started = self.start_cashier_frontend()
            
            # 4. Programar apertura del navegador
            self.wait_and_open_browser()
            
            # 5. Mostrar información
            logger.info("")
            logger.info("=" * 50)
            logger.info("SISTEMA CAJERO INICIADO")
            logger.info("=" * 50)
            logger.info(f"Backend API: {self.api_url}")
            logger.info(f"Documentación: {self.api_url}/docs")
            
            if frontend_started:
                logger.info(f"Frontend Cajero: {self.frontend_url}")
            else:
                logger.info("Frontend Cajero: No disponible (usando API directamente)")
            
            logger.info("")
            logger.info("🛒 Sistema listo para ventas!")
            logger.info("📱 La interfaz se abrirá automáticamente en el navegador")
            logger.info("")
            
            # 6. Mantener el script activo
            try:
                while True:
                    # Verificar que el API siga corriendo
                    if self.api_process and self.api_process.poll() is not None:
                        logger.error("Backend API se detuvo inesperadamente")
                        break
                    
                    time.sleep(30)  # Verificar cada 30 segundos
                    
            except KeyboardInterrupt:
                logger.info("Recibida señal de interrupción")
            
            return True
            
        except Exception as e:
            logger.error(f"Error durante inicio automático: {e}")
            return False
        
        finally:
            self.cleanup()


def main():
    """Función principal"""
    try:
        # Cambiar al directorio del proyecto
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        # Inicializar y ejecutar sistema cajero
        cashier_system = CashierAutoStart()
        success = cashier_system.run()
        
        if not success:
            logger.error("Error durante el inicio del sistema cajero")
            # En modo automático, no pausar
            # input("Presiona Enter para salir...")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()