@echo off
chcp 65001 >nul 2>&1
title POS Sistema Escaner - Lanzamiento Simple
color 0A

echo.
echo ================================================================
echo                    SISTEMA POS SIMPLIFICADO
echo                    PANTALLA COMPLETA DIRECTA
echo ================================================================
echo.
echo [%time%] Iniciando frontend POS...
echo [%time%] Modo: Solo interfaz (sin API backend)
echo.

REM Cambiar al directorio del frontend
cd /d "C:\InventarioBarras\frontend-pos"

REM Verificar que existe el servidor
if not exist "pos_server.py" (
    echo ERROR: pos_server.py no encontrado
    pause
    exit /b 1
)

echo [%time%] Iniciando servidor POS en puerto 3002...
echo [%time%] Interface disponible en: http://localhost:3002/pos
echo.
echo NOTA: El navegador se abrira automaticamente en pantalla completa
echo       Para cerrar: Presiona Ctrl+C en esta ventana
echo.
echo ================================================================
echo.

REM Iniciar servidor en background y abrir navegador
start /min python pos_server.py

REM Esperar 5 segundos para que el servidor este listo
timeout /t 5 /nobreak >nul

echo [%time%] Abriendo navegador en pantalla completa...

REM Intentar con Chrome en modo kiosk
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "CHROME_PATH_X86=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set "EDGE_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
set "EDGE_PATH_X86=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if exist "%CHROME_PATH%" (
    echo [%time%] Usando Google Chrome en modo pantalla completa...
    start "" "%CHROME_PATH%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%CHROME_PATH_X86%" (
    echo [%time%] Usando Google Chrome x86 en modo pantalla completa...
    start "" "%CHROME_PATH_X86%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%EDGE_PATH%" (
    echo [%time%] Usando Microsoft Edge en modo pantalla completa...
    start "" "%EDGE_PATH%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

if exist "%EDGE_PATH_X86%" (
    echo [%time%] Usando Microsoft Edge x86 en modo pantalla completa...
    start "" "%EDGE_PATH_X86%" --kiosk --disable-infobars --disable-extensions --no-first-run http://localhost:3002/pos
    goto :navegador_abierto
)

REM Fallback: usar navegador por defecto
echo [%time%] Chrome/Edge no encontrado, usando navegador por defecto...
start http://localhost:3002/pos

:navegador_abierto
echo.
echo ================================================================
echo                    SISTEMA INICIADO
echo ================================================================
echo.
echo ✅ Frontend POS funcionando en: http://localhost:3002/pos
echo ✅ Navegador abierto en pantalla completa
echo.
echo 🎯 El sistema esta listo para usar
echo 🛑 Para cerrar: Presiona Ctrl+C
echo.
echo ================================================================

REM Mantener la ventana abierta
pause >nul