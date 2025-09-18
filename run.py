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
   python run.py                 # Ejecutar API
   python run.py --frontend      # Ejecutar frontend
   python run.py --init-db       # Inicializar BD
   python run.py --install       # Instalar dependencias
   python run.py --check-camera  # Verificar cámara
   python run.py --info          # Esta información

📖 Documentación:
   • API Docs: http://localhost:8000/docs
   • Frontend: http://localhost:8501
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
    parser.add_argument("--init-db", action="store_true", 
                       help="Inicializar base de datos")
    parser.add_argument("--install", action="store_true", 
                       help="Instalar dependencias")
    parser.add_argument("--check-camera", action="store_true", 
                       help="Verificar disponibilidad de cámara")
    parser.add_argument("--info", action="store_true", 
                       help="Mostrar información del proyecto")
    
    args = parser.parse_args()
    
    if args.frontend:
        run_frontend()
    elif args.init_db:
        init_database()
    elif args.install:
        install_dependencies()
    elif args.check_camera:
        check_camera()
    elif args.info:
        show_info()
    else:
        # Por defecto, ejecutar la API
        run_api()


if __name__ == "__main__":
    main()