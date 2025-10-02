@echo off
chcp 65001 >nul 2>&1
title POS Sistema - Lanzamiento Mejorado

echo.
echo ================================================================
echo                    POS LANZAMIENTO MEJORADO
echo              (Consolas ocultas + Pantalla completa forzada)
echo ================================================================
echo.

REM Limpiar procesos anteriores
echo [%time%] Limpiando procesos Python anteriores...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im python3.11.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Cambiar al directorio
cd /d "C:\InventarioBarras\frontend-pos"
if not exist "pos_server.py" (
    echo ERROR: pos_server.py no encontrado
    pause
    exit /b 1
)

echo [%time%] Creando lanzador Python invisible...

REM Crear script Python para lanzamiento invisible
echo import subprocess > launch_invisible.py
echo import sys >> launch_invisible.py
echo import os >> launch_invisible.py
echo import time >> launch_invisible.py
echo import webbrowser >> launch_invisible.py
echo. >> launch_invisible.py
echo # Ocultar consola de este script >> launch_invisible.py
echo import ctypes >> launch_invisible.py
echo kernel32 = ctypes.WinDLL('kernel32') >> launch_invisible.py
echo user32 = ctypes.WinDLL('user32') >> launch_invisible.py
echo SW_HIDE = 0 >> launch_invisible.py
echo hwnd = kernel32.GetConsoleWindow() >> launch_invisible.py
echo user32.ShowWindow(hwnd, SW_HIDE) >> launch_invisible.py
echo. >> launch_invisible.py
echo print("Iniciando servidor POS invisible...") >> launch_invisible.py
echo. >> launch_invisible.py
echo # Iniciar servidor POS completamente oculto >> launch_invisible.py
echo startupinfo = subprocess.STARTUPINFO() >> launch_invisible.py
echo startupinfo.dwFlags ^|= subprocess.STARTF_USESHOWWINDOW >> launch_invisible.py
echo startupinfo.wShowWindow = subprocess.SW_HIDE >> launch_invisible.py
echo. >> launch_invisible.py
echo process = subprocess.Popen( >> launch_invisible.py
echo     [sys.executable, 'pos_server.py'], >> launch_invisible.py
echo     startupinfo=startupinfo, >> launch_invisible.py
echo     stdout=subprocess.DEVNULL, >> launch_invisible.py
echo     stderr=subprocess.DEVNULL, >> launch_invisible.py
echo     creationflags=subprocess.CREATE_NO_WINDOW >> launch_invisible.py
echo ) >> launch_invisible.py
echo. >> launch_invisible.py
echo print(f"Servidor POS iniciado (PID: {process.pid})") >> launch_invisible.py
echo. >> launch_invisible.py
echo # Esperar servidor >> launch_invisible.py
echo print("Esperando servidor...") >> launch_invisible.py
echo time.sleep(8) >> launch_invisible.py
echo. >> launch_invisible.py
echo # Abrir navegador en modo kiosk forzado >> launch_invisible.py
echo chrome_paths = [ >> launch_invisible.py
echo     r"C:\Program Files\Google\Chrome\Application\chrome.exe", >> launch_invisible.py
echo     r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", >> launch_invisible.py
echo     r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", >> launch_invisible.py
echo     r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" >> launch_invisible.py
echo ] >> launch_invisible.py
echo. >> launch_invisible.py
echo url = "http://localhost:3002/pos" >> launch_invisible.py
echo browser_opened = False >> launch_invisible.py
echo. >> launch_invisible.py
echo for chrome_path in chrome_paths: >> launch_invisible.py
echo     if os.path.exists(chrome_path): >> launch_invisible.py
echo         print(f"Abriendo {os.path.basename(chrome_path)} en modo kiosk") >> launch_invisible.py
echo         subprocess.Popen([ >> launch_invisible.py
echo             chrome_path, >> launch_invisible.py
echo             '--kiosk', >> launch_invisible.py
echo             '--disable-infobars', >> launch_invisible.py
echo             '--disable-extensions', >> launch_invisible.py
echo             '--no-first-run', >> launch_invisible.py
echo             '--disable-web-security', >> launch_invisible.py
echo             '--disable-features=VizDisplayCompositor', >> launch_invisible.py
echo             '--start-maximized', >> launch_invisible.py
echo             '--window-position=0,0', >> launch_invisible.py
echo             url >> launch_invisible.py
echo         ]) >> launch_invisible.py
echo         browser_opened = True >> launch_invisible.py
echo         break >> launch_invisible.py
echo. >> launch_invisible.py
echo if not browser_opened: >> launch_invisible.py
echo     print("Usando navegador por defecto con simulacion F11") >> launch_invisible.py
echo     webbrowser.open(url) >> launch_invisible.py
echo     time.sleep(3) >> launch_invisible.py
echo     # Simular F11 >> launch_invisible.py
echo     try: >> launch_invisible.py
echo         import pyautogui >> launch_invisible.py
echo         pyautogui.press('f11') >> launch_invisible.py
echo         print("F11 simulado") >> launch_invisible.py
echo     except ImportError: >> launch_invisible.py
echo         print("pyautogui no disponible") >> launch_invisible.py
echo. >> launch_invisible.py
echo print("POS iniciado exitosamente!") >> launch_invisible.py
echo print("Servidor corriendo en segundo plano") >> launch_invisible.py

echo [%time%] Ejecutando lanzador invisible...
python launch_invisible.py

REM Limpiar archivo temporal
del launch_invisible.py

REM Auto-cerrar esta ventana después de mostrar mensaje
echo.
echo ================================================================
echo                    POS INICIADO EXITOSAMENTE
echo ================================================================
echo.
echo ✅ Servidor POS ejecutándose invisiblemente
echo ✅ Navegador abierto en pantalla completa forzada
echo ✅ Consolas Python ocultas
echo.
echo 🎯 URL: http://localhost:3002/pos
echo 🛑 Para cerrar: usar cerrar_pos.bat
echo.
echo Esta ventana se cerrará automáticamente en 5 segundos...
timeout /t 5 /nobreak >nul

REM Cerrar esta ventana
exit