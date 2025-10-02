@echo off
chcp 65001 >nul 2>&1
title POS Pantalla Completa - Métodos Avanzados
color 0B

echo.
echo ================================================================
echo           POS SISTEMA ESCANER - PANTALLA COMPLETA
echo                    (Múltiples Métodos)
echo ================================================================
echo.
echo Selecciona el método de pantalla completa:
echo.
echo 1. KIOSK MODE (Recomendado - Profesional)
echo    - Pantalla completa total, sin escape
echo    - Perfecto para POS en producción
echo.
echo 2. FULLSCREEN MODE (Desarrollo)
echo    - Pantalla completa, permite Escape
echo    - Mejor para pruebas y desarrollo
echo.
echo 3. F11 SIMULADO (Compatible)
echo    - Simula tecla F11 automáticamente
echo    - Funciona con cualquier navegador
echo.
echo 4. AUTO-DETECTAR (Inteligente)
echo    - Usa kiosk si encuentra Chrome/Edge
echo    - Fallback a F11 simulado
echo.
set /p choice="Ingresa tu opción (1-4): "

REM Cambiar al directorio del frontend
cd /d "C:\InventarioBarras\frontend-pos"

REM Verificar que existe el servidor
if not exist "pos_server.py" (
    echo ERROR: pos_server.py no encontrado
    pause
    exit /b 1
)

echo.
echo [%time%] Iniciando servidor POS...
REM Iniciar servidor oculto
echo Set objShell = CreateObject("WScript.Shell") > launch_hidden.vbs
echo objShell.Run "python pos_server.py", 0, False >> launch_hidden.vbs
cscript launch_hidden.vbs >nul 2>&1
del launch_hidden.vbs

REM Esperar servidor
echo [%time%] Esperando servidor (6 segundos)...
timeout /t 6 /nobreak >nul

REM Aplicar método seleccionado
if "%choice%"=="1" goto :kiosk_mode
if "%choice%"=="2" goto :fullscreen_mode
if "%choice%"=="3" goto :f11_simulation
if "%choice%"=="4" goto :auto_detect

REM Por defecto, usar auto-detect
goto :auto_detect

:kiosk_mode
echo [%time%] Método: KIOSK MODE (Pantalla completa profesional)
call :open_browser_kiosk
goto :end

:fullscreen_mode
echo [%time%] Método: FULLSCREEN MODE (Desarrollo)
call :open_browser_fullscreen
goto :end

:f11_simulation
echo [%time%] Método: F11 SIMULADO (Compatible)
call :open_browser_f11
goto :end

:auto_detect
echo [%time%] Método: AUTO-DETECTAR (Inteligente)
call :open_browser_auto
goto :end

REM ================================================================
REM FUNCIONES DE LANZAMIENTO
REM ================================================================

:open_browser_kiosk
set "url=http://localhost:3002/pos"
set "chrome1=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "chrome2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set "edge1=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
set "edge2=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if exist "%chrome1%" (
    echo ✅ Usando Chrome - Modo KIOSK
    start "" "%chrome1%" --kiosk --disable-infobars --disable-extensions --no-first-run %url%
    exit /b
)
if exist "%chrome2%" (
    echo ✅ Usando Chrome x86 - Modo KIOSK  
    start "" "%chrome2%" --kiosk --disable-infobars --disable-extensions --no-first-run %url%
    exit /b
)
if exist "%edge1%" (
    echo ✅ Usando Edge - Modo KIOSK
    start "" "%edge1%" --kiosk --disable-infobars --disable-extensions --no-first-run %url%
    exit /b
)
if exist "%edge2%" (
    echo ✅ Usando Edge x86 - Modo KIOSK
    start "" "%edge2%" --kiosk --disable-infobars --disable-extensions --no-first-run %url%
    exit /b
)
echo ❌ Chrome/Edge no encontrado - Usando navegador por defecto
start %url%
exit /b

:open_browser_fullscreen
set "url=http://localhost:3002/pos"
set "chrome1=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "chrome2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%chrome1%" (
    echo ✅ Usando Chrome - Modo FULLSCREEN
    start "" "%chrome1%" --start-fullscreen --app=%url%
    exit /b
)
if exist "%chrome2%" (
    echo ✅ Usando Chrome x86 - Modo FULLSCREEN
    start "" "%chrome2%" --start-fullscreen --app=%url%
    exit /b
)
echo ✅ Navegador por defecto - Modo FULLSCREEN
start %url%
timeout /t 3 /nobreak >nul
call :simulate_f11
exit /b

:open_browser_f11
echo ✅ Abriendo navegador y simulando F11...
start http://localhost:3002/pos
timeout /t 4 /nobreak >nul
call :simulate_f11
exit /b

:open_browser_auto
REM Detectar navegador y usar mejor método
set "chrome1=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "chrome2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%chrome1%" (
    echo ✅ Auto-detectado: Chrome - Usando KIOSK
    call :open_browser_kiosk
    exit /b
)
if exist "%chrome2%" (
    echo ✅ Auto-detectado: Chrome x86 - Usando KIOSK  
    call :open_browser_kiosk
    exit /b
)
echo ✅ Auto-detectado: Navegador genérico - Usando F11
call :open_browser_f11
exit /b

:simulate_f11
REM Crear script PowerShell para simular F11
echo Add-Type -AssemblyName System.Windows.Forms > simulate_f11.ps1
echo [System.Windows.Forms.SendKeys]::SendWait("{F11}") >> simulate_f11.ps1
powershell -WindowStyle Hidden -File simulate_f11.ps1
del simulate_f11.ps1
echo ✅ F11 simulado
exit /b

:end
echo.
echo ================================================================
echo                   POS INICIADO EXITOSAMENTE
echo ================================================================
echo.
echo ✅ Servidor POS en segundo plano
echo ✅ Navegador en pantalla completa
echo 🎯 URL: http://localhost:3002/pos
echo.
echo Para cerrar: usa cerrar_pos.bat o Administrador de Tareas
echo.
pause