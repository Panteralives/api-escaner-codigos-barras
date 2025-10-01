#!/usr/bin/env python3
"""
Script de inicio rápido para el API Escáner de Códigos de Barras

Uso:
    python run.py                    # Ejecutar API
    python run.py --frontend         # Ejecutar frontend Streamlit
    python run.py --init-db          # Inicializar base de datos
    python run.py --help             # Mostrar ayuda
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_api():
    """Ejecutar la API FastAPI"""
    print("🚀 Iniciando API Escáner de Códigos de Barras...")
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("🏥 Health check en: http://localhost:8000/health")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 API detenida")


def run_frontend():
    """Ejecutar el frontend Streamlit"""
    print("🎨 Iniciando frontend Streamlit...")
    print("📱 Interfaz disponible en: http://localhost:8501")
    print("⚠️  Asegúrate de que la API esté ejecutándose en http://localhost:8000")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit",
            "run",
            "src/frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend detenido")


def run_web_frontend():
    """Ejecutar el frontend FastAPI Web"""
    print("🌐 Iniciando frontend FastAPI Web...")
    print("📱 Interfaz disponible en: http://localhost:3001")
    print("🔗 Rutas disponibles: /, /scan, /productos, /login")
    print("⚠️  Asegúrate de que la API esté ejecutándose en http://localhost:8000")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.frontend.web_app:app",
            "--host", "127.0.0.1",
            "--port", "3001",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend Web detenido")


def init_database():
    """Inicializar la base de datos"""
    print("🔧 Inicializando base de datos...")
    
    try:
        from src.db.init_db import init_database as init_db
        init_db()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        sys.exit(1)


def install_dependencies():
    """Instalar dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        sys.exit(1)


def check_camera():
    """Verificar disponibilidad de cámara"""
    print("📷 Verificando disponibilidad de cámara...")
    
    try:
        from src.scanner.barcode_scanner import BarcodeScanner
        
        if BarcodeScanner.is_camera_available(0):
            print("✅ Cámara disponible (índice 0)")
        else:
            print("⚠️  Cámara no disponible en índice 0")
            print("💡 Consejos:")
            print("   - Conecta una webcam USB")
            print("   - Cierra otras aplicaciones que puedan usar la cámara")
            print("   - Verifica que los drivers estén instalados")
    except Exception as e:
        print(f"❌ Error al verificar cámara: {e}")


def run_production_mode():
    """Ejecutar en modo producción: API + Frontend fullscreen"""
    import threading
    import time
    
    print("🏭 Iniciando modo PRODUCCIÓN...")
    print("🔒 Configuración: Sin reload, pantalla completa")
    print("-" * 50)
    
    def start_api():
        """Iniciar API en modo producción"""
        try:
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "src.api.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--log-level", "warning",  # Menos logs en producción
                "--no-access-log"  # Sin logs de acceso
            ])
        except KeyboardInterrupt:
            print("🛑 API detenida")
    
    def start_frontend():
        """Iniciar frontend en modo kiosk"""
        time.sleep(10)  # Esperar a que inicie la API
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit",
                "run",
                "src/frontend/streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "localhost",
                "--server.headless", "true",  # Sin interfaz de configuración
                "--browser.gatherUsageStats", "false"  # Sin estadísticas
            ])
        except KeyboardInterrupt:
            print("🛑 Frontend detenido")
    
    # Iniciar API en hilo separado
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Iniciar frontend
    start_frontend()


def setup_windows_autostart():
    """Configurar inicio automático en Windows"""
    import winreg
    import os
    
    print("⚙️ Configurando inicio automático...")
    
    try:
        # Ruta al script actual
        script_path = os.path.abspath(__file__)
        project_path = os.path.dirname(script_path)
        
        # Comando para ejecutar en modo producción
        command = f'python "{script_path}" --production'
        
        # Agregar al registro de Windows
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key, 
            "InventarioBarras",  # Nombre de la entrada
            0,
            winreg.REG_SZ,
            command
        )
        
        winreg.CloseKey(key)
        
        print("✅ Inicio automático configurado exitosamente")
        print(f"📍 Comando: {command}")
        print("📝 Para desactivar: Administrador de tareas > Inicio")
        
    except Exception as e:
        print(f"❌ Error configurando inicio automático: {e}")
        print("💡 Alternativa: Usar start_production.bat en carpeta de inicio")


def test_usb_hid_scanner():
    """Probar lector de códigos USB que funciona como teclado"""
    print("🗜️ Probando scanner USB-HID (funciona como teclado)...")
    print("=" * 60)
    
    try:
        # Importar el módulo del scanner HID
        from src.scanner.usb_hid_scanner import USBHIDScanner
        
        # Crear instancia
        scanner = USBHIDScanner()
        
        # Mostrar estado
        status = scanner.get_status()
        print(f"📊 Estado del scanner: {status}")
        
        if not status['keyboard_library']:
            print("❌ Error: Biblioteca 'keyboard' no disponible")
            print("📋 Instala con: pip install keyboard")
            return
        
        print("\n📝 INSTRUCCIONES:")
        print("1. Asegúrate de que el scanner USB esté conectado")
        print("2. Escanea un código de barras cuando se indique")
        print("3. El sistema detectará automáticamente el código")
        print("\n⚠️ IMPORTANTE: Este programa necesita permisos de administrador")
        print("para capturar eventos de teclado globalmente.")
        
        # Preguntar si continuar
        input("\n⏵️ Presiona Enter para continuar o Ctrl+C para cancelar...")
        
        # Probar el scanner con timeout de 30 segundos
        result = scanner.test_scanner(timeout_seconds=30)
        
        if result:
            print(f"\n✅ ¡SCANNER FUNCIONANDO!")
            print(f"📷 Código detectado: '{result}'")
            print(f"📈 Longitud: {len(result)} caracteres")
        else:
            print(f"\n❌ No se detectó ningún código")
            print("💡 Consejos:")
            print("   - Verifica que el scanner esté conectado")
            print("   - Prueba escanear en el Bloc de notas primero")
            print("   - Asegúrate de tener permisos de administrador")
            
    except ImportError as e:
        print(f"❌ Error importando módulo del scanner: {e}")
    except PermissionError:
        print("❌ Error de permisos: Ejecuta como Administrador")
        print("📝 Clic derecho en PowerShell → 'Ejecutar como administrador'")
    except KeyboardInterrupt:
        print("\n🛑 Prueba cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Prueba de scanner completada")


def check_all_hardware():
    """Verificar todo el hardware: cámara, puertos seriales, etc."""
    print("🔍 Verificando hardware del sistema...")
    print("=" * 50)
    
    # Verificar cámara
    print("📷 Verificando cámara...")
    try:
        from src.scanner.barcode_scanner import BarcodeScanner
        if BarcodeScanner.is_camera_available(0):
            print("✅ Cámara disponible (índice 0)")
        else:
            print("⚠️ Cámara no disponible")
    except Exception as e:
        print(f"❌ Error verificando cámara: {e}")
    
    # Verificar puertos seriales
    print("\n🔌 Verificando puertos seriales...")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        if ports:
            for port in ports:
                print(f"✅ {port.device}: {port.description}")
        else:
            print("⚠️ No se encontraron puertos seriales")
            
    except Exception as e:
        print(f"❌ Error verificando puertos: {e}")
    
    # Verificar espacio en disco
    print("\n💾 Verificando espacio en disco...")
    try:
        import psutil
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        total_gb = disk_usage.total / (1024**3)
        
        print(f"✅ Espacio libre: {free_gb:.1f} GB de {total_gb:.1f} GB")
        
        if free_gb < 1:
            print("⚠️ Advertencia: Poco espacio libre en disco")
            
    except Exception as e:
        print(f"❌ Error verificando disco: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Verificación de hardware completada")


def show_info():
    """Mostrar información del proyecto"""
    print("""
🔍 API Escáner de Códigos de Barras
═══════════════════════════════════

📋 Descripción:
   API completa para escanear códigos de barras usando Python,
   FastAPI, OpenCV, y Streamlit. Incluye autenticación JWT,
   gestión de productos, y soporte para cámaras USB reales.

🛠️  Tecnologías:
   • FastAPI - API REST rápida y moderna
   • SQLAlchemy + SQLite - Base de datos ORM
   • OpenCV + pyzbar - Escaneo de códigos de barras
   • Streamlit - Frontend web interactivo
   • JWT - Autenticación segura

📁 Estructura del proyecto:
   src/
   ├── api/          # Endpoints de la API
   ├── db/           # Modelos y base de datos
   ├── scanner/      # Lógica de escaneo
   └── frontend/     # Interfaz Streamlit

🚀 Comandos disponibles:
   python run.py                 # Ejecutar API (desarrollo)
   python run.py --frontend      # Ejecutar frontend Streamlit
   python run.py --web-frontend  # Ejecutar frontend FastAPI Web (recomendado)
   python run.py --production    # Modo PRODUCCIÓN (API + Frontend)
   python run.py --init-db       # Inicializar BD
   python run.py --install       # Instalar dependencias
   python run.py --check-camera  # Verificar cámara
   python run.py --check-hardware # Verificar todo el hardware
   python run.py --test-scanner  # Probar scanner USB (como teclado)
   python run.py --setup-autostart # Configurar inicio automático
   python run.py --info          # Esta información

📝 Documentación:
   • API Docs: http://localhost:8000/docs
   • Frontend Streamlit: http://localhost:8501
   • Frontend Web: http://localhost:3001 (con rutas /scan, /productos)
   • Health: http://localhost:8000/health

🔐 Credenciales por defecto:
   Usuario: admin
   Contraseña: admin123
    """)


def main():
    parser = argparse.ArgumentParser(
        description="Script de inicio para API Escáner de Códigos de Barras",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--frontend", action="store_true", 
                       help="Ejecutar frontend Streamlit")
    parser.add_argument("--web-frontend", action="store_true", 
                       help="Ejecutar frontend FastAPI Web (con rutas /scan, /productos)")
    parser.add_argument("--init-db", action="store_true", 
                       help="Inicializar base de datos")
    parser.add_argument("--install", action="store_true", 
                       help="Instalar dependencias")
    parser.add_argument("--check-camera", action="store_true", 
                       help="Verificar disponibilidad de cámara")
    parser.add_argument("--info", action="store_true", 
                       help="Mostrar información del proyecto")
    parser.add_argument("--production", action="store_true", 
                       help="Ejecutar en modo producción (fullscreen, sin reload)")
    parser.add_argument("--setup-autostart", action="store_true", 
                       help="Configurar inicio automático en Windows")
    parser.add_argument("--check-hardware", action="store_true", 
                       help="Verificar todo el hardware conectado")
    parser.add_argument("--test-scanner", action="store_true", 
                       help="Probar lector de códigos USB (como teclado)")
    
    args = parser.parse_args()
    
    if args.frontend:
        run_frontend()
    elif args.web_frontend:
        run_web_frontend()
    elif args.init_db:
        init_database()
    elif args.install:
        install_dependencies()
    elif args.check_camera:
        check_camera()
    elif args.info:
        show_info()
    elif args.production:
        run_production_mode()
    elif args.setup_autostart:
        setup_windows_autostart()
    elif args.check_hardware:
        check_all_hardware()
    elif args.test_scanner:
        test_usb_hid_scanner()
    else:
        # Por defecto, ejecutar la API
        run_api()


if __name__ == "__main__":
    main()