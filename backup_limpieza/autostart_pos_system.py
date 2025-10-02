#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA POS AVANZADO - INICIO AUTOMATICO
===============================================

Script optimizado para inicio automático en Windows.
Inicia el backend, frontend y abre la interfaz web lista para trabajar.

Autor: Claude AI Assistant
Fecha: 01 de Octubre, 2025
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

# Configuración de logging sin emojis para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autostart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class POSAutoStart:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8501"  # Streamlit
        self.pos_frontend_url = "http://localhost:3002"  # POS Avanzado
        
        self.api_process = None
        self.frontend_process = None
        self.pos_process = None
        
        # Configurar manejo de señales para cierre limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Manejo de señales para cierre limpio"""
        logger.info("Recibida señal de cierre, terminando procesos...")
        self.cleanup()
        sys.exit(0)
    
    def check_dependencies(self):
        """Verificar que las dependencias estén instaladas"""
        logger.info("Verificando dependencias del sistema...")
        
        # Verificar Python
        try:
            python_version = subprocess.run([sys.executable, "--version"], 
                                          capture_output=True, text=True)
            logger.info(f"Python: {python_version.stdout.strip()}")
        except Exception as e:
            logger.error(f"Error verificando Python: {e}")
            return False
        
        # Verificar dependencias críticas
        critical_deps = ['fastapi', 'uvicorn', 'streamlit', 'sqlalchemy']
        
        for dep in critical_deps:
            try:
                subprocess.run([sys.executable, "-c", f"import {dep}"], 
                             check=True, capture_output=True)
                logger.info(f"Dependencia OK: {dep}")
            except subprocess.CalledProcessError:
                logger.error(f"Dependencia faltante: {dep}")
                logger.info("Instalando dependencias...")
                self.install_dependencies()
                break
        
        return True
    
    def install_dependencies(self):
        """Instalar dependencias si faltan"""
        logger.info("Instalando dependencias del proyecto...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, cwd=self.project_dir)
            logger.info("Dependencias instaladas correctamente")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error instalando dependencias: {e}")
            return False
        return True
    
    def wait_for_api(self, max_attempts=20, delay=3):
        """Esperar a que la API esté disponible"""
        logger.info("Esperando a que la API esté disponible...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("API está disponible")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Intento {attempt + 1}/{max_attempts} - API no disponible, reintentando...")
            time.sleep(delay)
        
        logger.warning("API no respondió después de todos los intentos")
        return False
    
    def start_api(self):
        """Iniciar el servidor API"""
        logger.info("Iniciando servidor API...")
        
        try:
            # Usar run.py que maneja correctamente las importaciones relativas
            run_py = self.project_dir / "run.py"
            if run_py.exists():
                cmd = [sys.executable, "run.py"]
            else:
                # Fallback: usar uvicorn directamente
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "src.api.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--log-level", "info"
                ]
            
            # Iniciar API en proceso separado
            self.api_process = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            logger.info(f"API iniciada con PID: {self.api_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando API: {e}")
            return False
    
    def start_pos_frontend(self):
        """Iniciar el frontend POS avanzado"""
        logger.info("Iniciando frontend POS avanzado...")
        
        try:
            pos_server = self.project_dir / "frontend-pos" / "pos_server.py"
            
            if pos_server.exists():
                self.pos_process = subprocess.Popen(
                    [sys.executable, str(pos_server)],
                    cwd=pos_server.parent,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                logger.info(f"Frontend POS iniciado con PID: {self.pos_process.pid}")
                return True
            else:
                logger.warning("Archivo pos_server.py no encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Error iniciando frontend POS: {e}")
            return False
    
    def start_streamlit_frontend(self):
        """Iniciar frontend Streamlit como backup"""
        logger.info("Iniciando frontend Streamlit...")
        
        try:
            streamlit_app = self.project_dir / "src" / "frontend" / "streamlit_app.py"
            
            if streamlit_app.exists():
                cmd = [
                    sys.executable, "-m", "streamlit", "run",
                    str(streamlit_app),
                    "--server.port", "8501",
                    "--server.address", "localhost",
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ]
                
                self.frontend_process = subprocess.Popen(
                    cmd,
                    cwd=self.project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                logger.info(f"Frontend Streamlit iniciado con PID: {self.frontend_process.pid}")
                return True
            else:
                logger.warning("Archivo streamlit_app.py no encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Error iniciando frontend Streamlit: {e}")
            return False
    
    def open_browser_fullscreen(self, url, delay=5):
        """Abrir navegador en pantalla completa con la interfaz"""
        logger.info(f"Abriendo navegador en PANTALLA COMPLETA: {url} (delay: {delay}s)")
        
        def open_delayed():
            time.sleep(delay)
            try:
                # Intentar con Chrome/Edge en modo kiosko (pantalla completa)
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                ]
                
                browser_opened = False
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        logger.info(f"Usando navegador: {os.path.basename(chrome_path)}")
                        
                        # Argumentos para modo pantalla completa
                        args = [
                            chrome_path,
                            "--kiosk",  # Modo pantalla completa
                            "--disable-infobars",
                            "--disable-extensions",
                            "--no-first-run",
                            "--disable-default-apps",
                            "--disable-popup-blocking",
                            "--start-maximized",
                            url
                        ]
                        
                        subprocess.Popen(args)
                        logger.info(f"Navegador abierto en pantalla completa: {url}")
                        browser_opened = True
                        break
                
                if not browser_opened:
                    # Fallback: usar navegador por defecto y simular F11
                    logger.info("Chrome/Edge no encontrado, usando navegador por defecto")
                    webbrowser.open(url, new=2)
                    
                    # Intentar simular F11 después de abrir
                    time.sleep(3)
                    try:
                        import pyautogui
                        pyautogui.press('f11')
                        logger.info("F11 simulado para pantalla completa")
                    except ImportError:
                        logger.warning("pyautogui no disponible - instalar con: pip install pyautogui")
                    except Exception as e:
                        logger.warning(f"No se pudo simular F11: {e}")
                        
            except Exception as e:
                logger.error(f"Error abriendo navegador: {e}")
        
        # Abrir en hilo separado para no bloquear
        thread = threading.Thread(target=open_delayed, daemon=True)
        thread.start()
    
    def cleanup(self):
        """Limpiar procesos al cerrar"""
        logger.info("Limpiando procesos...")
        
        for process_name, process in [
            ("API", self.api_process),
            ("Frontend", self.frontend_process),
            ("POS", self.pos_process)
        ]:
            if process and process.poll() is None:
                logger.info(f"Terminando proceso {process_name} (PID: {process.pid})")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Forzando cierre de {process_name}")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error cerrando {process_name}: {e}")
    
    def run(self):
        """Ejecutar inicio automático completo"""
        logger.info("=" * 60)
        logger.info("SISTEMA POS AVANZADO - INICIO AUTOMATICO")
        logger.info("=" * 60)
        logger.info(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Directorio: {self.project_dir}")
        
        try:
            # 1. Verificar dependencias
            if not self.check_dependencies():
                logger.error("Error en verificación de dependencias")
                return False
            
            # 2. Iniciar API
            if not self.start_api():
                logger.error("Error iniciando API")
                return False
            
            # 3. Esperar a que API esté disponible
            if not self.wait_for_api():
                logger.error("API no disponible")
                return False
            
            # 4. Iniciar frontend POS (prioritario)
            pos_started = self.start_pos_frontend()
            
            # 5. Si POS no está disponible, usar Streamlit
            if not pos_started:
                logger.info("Usando Streamlit como frontend alternativo")
                self.start_streamlit_frontend()
            
            # 6. Esperar un poco para que los servicios estén listos
            logger.info("Esperando a que los servicios estén listos...")
            time.sleep(10)
            
            # 7. Abrir interfaz web en PANTALLA COMPLETA
            if pos_started:
                logger.info("Abriendo interfaz POS avanzada en pantalla completa...")
                # Modificar URL para ir directamente a la interfaz POS
                pos_interface_url = f"{self.pos_frontend_url}/pos"
                self.open_browser_fullscreen(pos_interface_url, delay=3)
            else:
                logger.info("Abriendo interfaz Streamlit en pantalla completa...")
                self.open_browser_fullscreen(self.frontend_url, delay=3)
            
            # 8. Mostrar información del sistema
            logger.info("")
            logger.info("=" * 60)
            logger.info("SISTEMA INICIADO CORRECTAMENTE")
            logger.info("=" * 60)
            logger.info(f"API Backend:     {self.api_url}")
            logger.info(f"Documentación:   {self.api_url}/docs")
            logger.info(f"Health Check:    {self.api_url}/health")
            
            if pos_started:
                logger.info(f"Frontend POS:    {self.pos_frontend_url}")
            else:
                logger.info(f"Frontend Web:    {self.frontend_url}")
            
            logger.info("")
            logger.info("Sistema listo para trabajar!")
            logger.info("Presiona Ctrl+C para detener el sistema")
            logger.info("=" * 60)
            
            # 9. Mantener el script corriendo
            try:
                while True:
                    # Verificar que los procesos sigan corriendo
                    if self.api_process and self.api_process.poll() is not None:
                        logger.error("API se detuvo inesperadamente")
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
        
        # Inicializar y ejecutar sistema
        pos_system = POSAutoStart()
        success = pos_system.run()
        
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