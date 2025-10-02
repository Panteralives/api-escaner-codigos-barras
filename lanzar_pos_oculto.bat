@echo off
chcp 65001 >nul 2>&1
title POS Sistema Escaner - Modo Silencioso
color 0A

REM ================================================================
REM LANZADOR POS CON CONSOLAS OCULTAS
REM ================================================================
echo.
echo ================================================================
echo                    INICIANDO POS SILENCIOSO
echo                    (Consolas en segundo plano)
echo ================================================================
echo.
echo [%time%] Preparando lanzamiento silencioso...
echo [%time%] Las consolas se ocultaran automaticamente
echo.

REM Cambiar al directorio del frontend
cd /d "C:\InventarioBarras\frontend-pos"

REM Verificar que existe el servidor
if not exist "pos_server.py" (
    echo ERROR: pos_server.py no encontrado
    pause
    exit /b 1
)

REM Crear script VBS para lanzamiento silencioso
echo Set objShell = CreateObject("WScript.Shell") > launch_hidden.vbs
echo objShell.Run "python pos_server.py", 0, False >> launch_hidden.vbs

echo [%time%] Iniciando servidor POS (modo oculto)...
echo [%time%] Puerto: 3002
echo [%time%] URL: http://localhost:3002/pos
echo.

REM Ejecutar servidor en modo completamente oculto
cscript launch_hidden.vbs >nul 2>&1

REM Limpiar archivo temporal
del launch_hidden.vbs

REM Esperar que el servidor este listo
echo [%time%] Esperando servidor (8 segundos)...
timeout /t 8 /nobreak >nul

echo [%time%] Abriendo navegador en pantalla completa...

REM Detectar y usar navegador disponible
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "CHROME_PATH_X86=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set "EDGE_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
set "EDGE_PATH_X86=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if exist "%CHROME_PATH%" (
    echo [%time%] Google Chrome encontrado - Modo pantalla completa
    start "" "%CHROME_PATH%" --kiosk --disable-infobars --disable-extensions --no-first-run --disable-web-security --disable-features=VizDisplayCompositor http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%CHROME_PATH_X86%" (
    echo [%time%] Google Chrome x86 encontrado - Modo pantalla completa
    start "" "%CHROME_PATH_X86%" --kiosk --disable-infobars --disable-extensions --no-first-run --disable-web-security --disable-features=VizDisplayCompositor http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%EDGE_PATH%" (
    echo [%time%] Microsoft Edge encontrado - Modo pantalla completa
    start "" "%EDGE_PATH%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%EDGE_PATH_X86%" (
    echo [%time%] Microsoft Edge x86 encontrado - Modo pantalla completa
    start "" "%EDGE_PATH_X86%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

REM Fallback: navegador por defecto
echo [%time%] Usando navegador por defecto...
start http://localhost:3002/pos

:navegador_abierto
echo.
echo ================================================================
echo                    SISTEMA POS INICIADO
echo ================================================================
echo.
echo ✅ Servidor POS ejecutandose en segundo plano
echo ✅ Navegador abierto en pantalla completa
echo ✅ Consolas Python ocultas
echo.
echo 🎯 URL: http://localhost:3002/pos
echo 🎯 El sistema esta completamente funcional
echo.
echo ================================================================
echo.
echo 💡 INFORMACION IMPORTANTE:
echo    • El servidor POS corre invisiblemente
echo    • Para cerrar COMPLETAMENTE el sistema:
echo      1. Cierra el navegador
echo      2. Ve al Administrador de Tareas
echo      3. Termina procesos: python.exe (pos_server.py)
echo.
echo ⚠️  O usa el script de cierre: cerrar_pos.bat
echo.
echo ================================================================

REM Auto-minimizar esta ventana después de 10 segundos
echo [%time%] Esta ventana se minimizara en 10 segundos...
timeout /t 10 /nobreak >nul

REM Minimizar ventana usando PowerShell
powershell -WindowStyle Hidden -Command "Add-Type -Name 'Win32' -Namespace 'API' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);'; $consolePtr = [System.Diagnostics.Process]::GetCurrentProcess().MainWindowHandle; [API.Win32]::ShowWindow($consolePtr, 2)" 2>nul

REM Mantener el proceso vivo pero oculto
:mantener_vivo
timeout /t 30 >nul
goto :mantener_vivo