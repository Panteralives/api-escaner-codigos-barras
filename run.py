#!/usr/bin/env python3
"""
Script de inicio rápido para el API Escáner de Códigos de Barras

Uso:
    python run.py                    # Ejecutar API
    python run.py --frontend         # Ejecutar frontend Streamlit
    python run.py --web-frontend     # Ejecutar NUESTRO frontend de TPV
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


def run_pos_frontend():
    """Ejecutar el frontend del TPV con login"""
    print("🌐 Iniciando Frontend del TPV (ScanPay POS)...")
    print("📱 Interfaz disponible en: http://localhost:3002")
    print("🔒 Accede a / para ver el TPV o a /login para iniciar sesión")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        # Usamos sys.executable para garantizar que se usa el intérprete correcto
        # del entorno virtual actual.
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "frontend-pos.pos_server:app", # APUNTA A NUESTRO SERVIDOR
            "--host", "0.0.0.0",
            "--port", "3002",             # EN EL PUERTO CORRECTO
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend del TPV detenido")
    except Exception as e:
        print(f"❌ Error al iniciar el frontend del TPV: {e}")


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


def main():
    parser = argparse.ArgumentParser(
        description="Script de inicio para el sistema TPV",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--web-frontend", action="store_true", 
                       help="Ejecutar el frontend del TPV ScanPay POS")
    parser.add_argument("--init-db", action="store_true", 
                       help="Inicializar base de datos")
    # Se mantienen otros argumentos por si son necesarios, pero se simplifica el menú
    # para enfocarnos en el TPV
    
    args = parser.parse_args()
    
    if args.web_frontend:
        run_pos_frontend()
    elif args.init_db:
        init_database()
    else:
        # Por defecto, si no se especifica --web-frontend, mostramos ayuda.
        parser.print_help()


if __name__ == "__main__":
    main()
