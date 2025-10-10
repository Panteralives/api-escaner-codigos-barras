
import sys
import subprocess
import os
import time
import signal

# --- Configuración ---
PID_DIR = os.path.join(os.path.dirname(__file__), '.pids')
POS_SERVER_PID_FILE = os.path.join(PID_DIR, 'pos_server.pid')
WORKER_PID_FILE = os.path.join(PID_DIR, 'worker.pid')

# Obtener la ruta del intérprete de Python actual para evitar problemas de PATH
PYTHON_EXECUTABLE = sys.executable

def _ensure_pid_dir():
    """Asegura que el directorio para los archivos PID exista."""
    if not os.path.exists(PID_DIR):
        os.makedirs(PID_DIR)

def _get_pid(pid_file):
    """Lee un PID de un archivo."""
    try:
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    except (IOError, ValueError):
        return None

def _is_running(pid):
    """Verifica si un proceso con un PID dado está corriendo."""
    if pid is None:
        return False
    try:
        # signal.SIG_DFL es una forma no invasiva de comprobar si el proceso existe.
        # No envía ninguna señal real.
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def start():
    """Inicia el servidor TPV y el worker de facturación."""
    _ensure_pid_dir()
    
    # --- Iniciar Servidor TPV (Uvicorn) ---
    pos_pid = _get_pid(POS_SERVER_PID_FILE)
    if _is_running(pos_pid):
        print("✅ El servidor TPV ya está en ejecución.")
    else:
        print("🚀 Iniciando el servidor TPV...")
        pos_command = [
            PYTHON_EXECUTABLE, "-m", "uvicorn", 
            "frontend-pos.pos_server:app", 
            "--host", "0.0.0.0", 
            "--port", "3002",
            "--reload"
        ]
        pos_process = subprocess.Popen(pos_command, stdout=sys.stdout, stderr=sys.stderr)
        with open(POS_SERVER_PID_FILE, 'w') as f:
            f.write(str(pos_process.pid))
        print(f"✅ Servidor TPV iniciado con PID: {pos_process.pid}")

    time.sleep(2) # Dar un momento para que el primer servidor inicie

    # --- Iniciar Worker de Facturación ---
    worker_pid = _get_pid(WORKER_PID_FILE)
    if _is_running(worker_pid):
        print("✅ El worker de facturación ya está en ejecución.")
    else:
        print("🚀 Iniciando el worker de facturación...")
        worker_command = [PYTHON_EXECUTABLE, "src/payment/worker.py"]
        worker_process = subprocess.Popen(worker_command, stdout=sys.stdout, stderr=sys.stderr)
        with open(WORKER_PID_FILE, 'w') as f:
            f.write(str(worker_process.pid))
        print(f"✅ Worker de facturación iniciado con PID: {worker_process.pid}")

def stop():
    """Detiene todos los servicios gestionados."""
    
    # --- Detener Servidor TPV ---
    pos_pid = _get_pid(POS_SERVER_PID_FILE)
    if pos_pid and _is_running(pos_pid):
        print(f"🛑 Deteniendo el servidor TPV (PID: {pos_pid})...")
        try:
            os.kill(pos_pid, signal.SIGTERM)
            os.remove(POS_SERVER_PID_FILE)
            print("✅ Servidor TPV detenido.")
        except OSError as e:
            print(f"⚠️  Error al detener el servidor TPV: {e}")
            os.remove(POS_SERVER_PID_FILE) # Limpiar archivo PID de todos modos
    else:
        print("⚪ El servidor TPV no está en ejecución.")
        if os.path.exists(POS_SERVER_PID_FILE):
             os.remove(POS_SERVER_PID_FILE)

    # --- Detener Worker ---
    worker_pid = _get_pid(WORKER_PID_FILE)
    if worker_pid and _is_running(worker_pid):
        print(f"🛑 Deteniendo el worker (PID: {worker_pid})...")
        try:
            os.kill(worker_pid, signal.SIGTERM)
            os.remove(WORKER_PID_FILE)
            print("✅ Worker detenido.")
        except OSError as e:
            print(f"⚠️  Error al detener el worker: {e}")
            os.remove(WORKER_PID_FILE)
    else:
        print("⚪ El worker de facturación no está en ejecución.")
        if os.path.exists(WORKER_PID_FILE):
             os.remove(WORKER_PID_FILE)

def status():
    """Muestra el estado de los servicios."""
    print("--- Estado de los Servicios ---")
    
    # Estado del Servidor TPV
    pos_pid = _get_pid(POS_SERVER_PID_FILE)
    if _is_running(pos_pid):
        print(f"🟢 Servidor TPV: CORRIENDO (PID: {pos_pid})")
    else:
        print("🔴 Servidor TPV: DETENIDO")

    # Estado del Worker
    worker_pid = _get_pid(WORKER_PID_FILE)
    if _is_running(worker_pid):
        print(f"🟢 Worker de Facturación: CORRIENDO (PID: {worker_pid})")
    else:
        print("🔴 Worker de Facturación: DETENIDO")
    print("---------------------------")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python manage.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start()
    elif command == "stop":
        stop()
    elif command == "status":
        status()
    elif command == "restart":
        print("🔄 Reiniciando servicios...")
        stop()
        time.sleep(2)
        start()
    else:
        print(f"Comando desconocido: {command}")
        print("Uso: python manage.py [start|stop|status|restart]")
        sys.exit(1)
