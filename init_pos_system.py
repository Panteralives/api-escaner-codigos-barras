#!/usr/bin/env python3
"""
Script de inicialización integrado para ScanPay POS
Combina el frontend modular con el sistema de gestión avanzado
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

class POSSystemInitializer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.manage_script = self.base_dir / "manage.py"
        self.pos_frontend = self.base_dir / "pos_modular.html"
        
    def check_dependencies(self):
        """Verificar dependencias del sistema"""
        print("🔍 Verificando dependencias...")
        
        # Verificar Python
        print(f"✅ Python: {sys.version}")
        
        # Verificar manage.py
        if not self.manage_script.exists():
            print("❌ manage.py no encontrado")
            return False
        
        # Verificar frontend modular
        if not self.pos_frontend.exists():
            print("❌ Frontend modular no encontrado")
            return False
            
        print("✅ Todas las dependencias están disponibles")
        return True
    
    def start_pos_server(self):
        """Iniciar el servidor POS usando manage.py"""
        print("🚀 Iniciando servidor POS...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.manage_script), 
                "start"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Servidor POS iniciado exitosamente")
                print(result.stdout)
                return True
            else:
                print("❌ Error iniciando servidor POS:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout iniciando servidor POS")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    def wait_for_server(self, max_attempts=10):
        """Esperar a que el servidor esté disponible"""
        print("⏳ Esperando que el servidor esté listo...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:3002/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Servidor POS está respondiendo")
                    return True
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    print(f"⏳ Intento {attempt + 1}/{max_attempts} - Esperando...")
                    time.sleep(3)
                else:
                    print("❌ Servidor no responde después de varios intentos")
        
        return False
    
    def open_frontend(self):
        """Abrir el frontend modular"""
        print("🌐 Abriendo frontend POS...")
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(self.pos_frontend))
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', 
                              str(self.pos_frontend)])
            
            print("✅ Frontend abierto en navegador")
            return True
            
        except Exception as e:
            print(f"❌ Error abriendo frontend: {e}")
            return False
    
    def show_system_status(self):
        """Mostrar estado del sistema"""
        print("\n" + "="*50)
        print("📊 ESTADO DEL SISTEMA SCANPAY POS")
        print("="*50)
        
        # Estado del servidor
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.manage_script), 
                "status"
            ], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
        
        # URLs disponibles
        print("\n🔗 URLs del sistema:")
        print("   • Servidor POS: http://localhost:3002")
        print("   • API Principal: http://localhost:8001")
        print("   • Frontend Modular: file://" + str(self.pos_frontend.absolute()))
        
        print("\n💡 Funcionalidades integradas:")
        print("   ✅ Autenticación y sesiones")
        print("   ✅ Escáner de códigos avanzado")
        print("   ✅ Facturación electrónica")
        print("   ✅ Gestión de inventario")
        print("   ✅ Sistema de pagos robusto")
        print("   ✅ Modo offline/standalone")
        
        print("\n🎮 Controles disponibles:")
        print("   • python manage.py start   - Iniciar servicios")
        print("   • python manage.py stop    - Detener servicios")  
        print("   • python manage.py status  - Ver estado")
        print("   • python manage.py restart - Reiniciar servicios")
        
        print("="*50)
    
    def run(self):
        """Ejecutar inicialización completa"""
        print("🚀 INICIALIZANDO SISTEMA SCANPAY POS")
        print("="*40)
        
        # Verificar dependencias
        if not self.check_dependencies():
            print("❌ Faltan dependencias. Abortando.")
            return False
        
        # Iniciar servidor
        if not self.start_pos_server():
            print("❌ No se pudo iniciar el servidor. Abortando.")
            return False
        
        # Esperar servidor
        if not self.wait_for_server():
            print("⚠️ El servidor puede no estar completamente listo.")
        
        # Abrir frontend
        self.open_frontend()
        
        # Mostrar estado
        time.sleep(2)
        self.show_system_status()
        
        print("\n🎉 ¡Sistema iniciado exitosamente!")
        print("👀 El frontend debería estar abierto en tu navegador")
        print("🔧 Usa 'python manage.py stop' para detener el sistema")
        
        return True

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stop":
            print("🛑 Deteniendo sistema POS...")
            manage_path = Path(__file__).parent / "manage.py"
            subprocess.run([sys.executable, str(manage_path), "stop"])
            return
        elif command == "status":
            print("📊 Estado del sistema POS...")
            manage_path = Path(__file__).parent / "manage.py"
            subprocess.run([sys.executable, str(manage_path), "status"])
            return
    
    # Inicialización completa
    initializer = POSSystemInitializer()
    success = initializer.run()
    
    if not success:
        print("\n❌ La inicialización falló.")
        sys.exit(1)

if __name__ == "__main__":
    main()