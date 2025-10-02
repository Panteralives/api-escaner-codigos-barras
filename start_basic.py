#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE INICIO BASICO - SISTEMA POS
=====================================

Script básico sin emojis para iniciar el sistema POS.
Compatible con Windows y codificación cp1252.

Autor: Claude AI Assistant
Fecha: 02 de Octubre, 2025
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import requests
from pathlib import Path
import signal
import logging
from datetime import datetime

# Configuración de logging sin emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('start_basic.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BasicPOSStarter:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.api_url = "http://localhost:8000"
        self.api_process = None
        
        # Configurar manejo de señales para cierre limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Manejo de señales para cierre limpio"""
        logger.info("Recibida señal de cierre, terminando procesos...")
        self.cleanup()
        sys.exit(0)
    
    def kill_existing_processes(self):
        """Terminar procesos Python existentes que puedan estar ocupando puertos"""
        logger.info("Buscando procesos Python usando puerto 8000...")
        try:
            # Encontrar qué proceso usa el puerto 8000
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, 
                text=True
            )
            
            current_pid = os.getpid()
            for line in result.stdout.split('\n'):
                if ":8000" in line and "LISTENING" in line:
                    # Extraer PID de la línea
                    pid_str = line.split()[-1]
                    try:
                        pid = int(pid_str)
                        if pid != current_pid:  # No matar el proceso actual
                            logger.info(f"Terminando proceso PID {pid} que usa puerto 8000")
                            subprocess.run(["taskkill", "/f", "/pid", str(pid)], 
                                         capture_output=True, check=False)
                    except ValueError:
                        continue
            
            time.sleep(3)  # Esperar a que los puertos se liberen
            logger.info("Procesos conflictivos terminados")
        except Exception as e:
            logger.warning(f"Error terminando procesos: {e}")
    
    def check_port_available(self, port=8000):
        """Verificar si un puerto está disponible"""
        try:
            result = subprocess.run(
                ["netstat", "-an"], 
                capture_output=True, 
                text=True
            )
            if f":{port}" in result.stdout and "LISTENING" in result.stdout:
                logger.warning(f"Puerto {port} ya está en uso")
                return False
            logger.info(f"Puerto {port} disponible")
            return True
        except Exception as e:
            logger.error(f"Error verificando puerto {port}: {e}")
            return False
    
    def start_api_basic(self):
        """Iniciar API usando el método más básico"""
        logger.info("Iniciando API...")
        
        try:
            # Usar el script run.py que ya funciona
            cmd = [sys.executable, "run.py"]
            
            # Iniciar API en proceso separado con nueva consola
            self.api_process = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,  # Nueva ventana
                shell=False
            )
            
            logger.info(f"API iniciada con PID: {self.api_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando API: {e}")
            return False
    
    def wait_for_api_basic(self, max_attempts=15, delay=2):
        """Esperar a que la API esté disponible"""
        logger.info("Esperando a que la API esté disponible...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("API está disponible y funcionando")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Intento {attempt + 1}/{max_attempts} - Esperando API...")
            time.sleep(delay)
        
        logger.error("API no está disponible después de todos los intentos")
        return False
    
    def open_browser_basic(self, url="http://localhost:8000/docs"):
        """Abrir navegador de forma básica"""
        logger.info(f"Abriendo navegador: {url}")
        
        def open_delayed():
            time.sleep(3)
            try:
                webbrowser.open(url, new=2)
                logger.info("Navegador abierto correctamente")
            except Exception as e:
                logger.error(f"Error abriendo navegador: {e}")
        
        thread = threading.Thread(target=open_delayed, daemon=True)
        thread.start()
    
    def run_diagnostic(self):
        """Ejecutar diagnóstico básico del sistema"""
        logger.info("=== DIAGNOSTICO DEL SISTEMA ===")
        
        # 1. Verificar Python
        logger.info(f"Python: {sys.version}")
        
        # 2. Verificar directorio
        logger.info(f"Directorio: {self.project_dir}")
        
        # 3. Verificar archivos principales
        files_to_check = ["run.py", "src/api/main.py", "config/app_config.json"]
        for file_path in files_to_check:
            full_path = self.project_dir / file_path
            status = "EXISTE" if full_path.exists() else "FALTA"
            logger.info(f"Archivo {file_path}: {status}")
        
        # 4. Verificar puerto
        port_available = self.check_port_available(8000)
        logger.info(f"Puerto 8000: {'LIBRE' if port_available else 'OCUPADO'}")
        
        # 5. Probar conexión a la API (si está corriendo)
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            logger.info(f"API Status: FUNCIONANDO (HTTP {response.status_code})")
        except:
            logger.info("API Status: NO DISPONIBLE")
        
        logger.info("=== FIN DIAGNOSTICO ===")
    
    def cleanup(self):
        """Limpiar procesos al cerrar"""
        logger.info("Limpiando procesos...")
        
        if self.api_process and self.api_process.poll() is None:
            logger.info(f"Terminando proceso API (PID: {self.api_process.pid})")
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Forzando cierre de API")
                self.api_process.kill()
            except Exception as e:
                logger.error(f"Error cerrando API: {e}")
    
    def run(self, diagnostic_only=False):
        """Ejecutar inicio básico"""
        logger.info("=" * 60)
        logger.info("SISTEMA POS - INICIO BASICO")
        logger.info("=" * 60)
        logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. Diagnóstico
            self.run_diagnostic()
            
            if diagnostic_only:
                return True
            
            # 2. Limpiar procesos anteriores
            self.kill_existing_processes()
            
            # 3. Verificar que el puerto esté libre
            if not self.check_port_available(8000):
                logger.error("Puerto 8000 no disponible. Usa el diagnostico para más info.")
                return False
            
            # 4. Iniciar API
            if not self.start_api_basic():
                logger.error("Error iniciando API")
                return False
            
            # 5. Esperar a que API esté disponible
            if not self.wait_for_api_basic():
                logger.error("API no disponible")
                return False
            
            # 6. Abrir navegador
            self.open_browser_basic()
            
            # 7. Mostrar información
            logger.info("")
            logger.info("=" * 60)
            logger.info("SISTEMA INICIADO CORRECTAMENTE")
            logger.info("=" * 60)
            logger.info(f"API Backend: {self.api_url}")
            logger.info(f"Documentacion: {self.api_url}/docs")
            logger.info(f"Health Check: {self.api_url}/health")
            logger.info("")
            logger.info("Sistema listo para trabajar!")
            logger.info("Para detener: Cierra esta ventana o presiona Ctrl+C")
            logger.info("=" * 60)
            
            # 8. Mantener corriendo
            try:
                while True:
                    # Verificar que la API siga corriendo
                    if self.api_process and self.api_process.poll() is not None:
                        logger.error("API se detuvo inesperadamente")
                        break
                    
                    time.sleep(30)  # Verificar cada 30 segundos
                    
            except KeyboardInterrupt:
                logger.info("Recibida señal de interrupción del usuario")
            
            return True
            
        except Exception as e:
            logger.error(f"Error durante inicio: {e}")
            return False
        
        finally:
            self.cleanup()


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inicio básico del Sistema POS")
    parser.add_argument("--diagnostic", "-d", action="store_true", 
                       help="Solo ejecutar diagnóstico sin iniciar servicios")
    
    args = parser.parse_args()
    
    try:
        # Cambiar al directorio del proyecto
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        # Inicializar y ejecutar sistema
        pos_starter = BasicPOSStarter()
        success = pos_starter.run(diagnostic_only=args.diagnostic)
        
        if not success:
            logger.error("Error durante el inicio del sistema")
            input("Presiona Enter para salir...")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()