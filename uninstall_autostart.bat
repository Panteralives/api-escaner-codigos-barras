@echo off
REM ================================================================
REM 🗑️ DESINSTALADOR DE INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
REM ================================================================

title Desinstalador Inicio Automático - Sistema POS

echo.
echo ================================================================
echo   DESINSTALADOR DE INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
echo ================================================================
echo.

echo [INFO] Buscando configuraciones de inicio automático...
echo.

REM Variables
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_FOLDER%\Sistema POS Avanzado.lnk
set KEY_PATH=HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
set VALUE_NAME=SistemaPOSAvanzado

set FOUND=0

REM Verificar acceso directo en carpeta de inicio
if exist "%SHORTCUT_PATH%" (
    echo [ENCONTRADO] Acceso directo: %SHORTCUT_PATH%
    set FOUND=1
) else (
    echo [NO ENCONTRADO] Acceso directo en carpeta Startup
)

REM Verificar entrada en registro
reg query "%KEY_PATH%" /v "%VALUE_NAME%" >nul 2>&1
if errorlevel 0 (
    echo [ENCONTRADO] Entrada de registro: %KEY_PATH%\%VALUE_NAME%
    set FOUND=1
) else (
    echo [NO ENCONTRADO] Entrada en registro
)

echo.

if %FOUND%==0 (
    echo ================================================================
    echo                    NO HAY NADA QUE DESINSTALAR
    echo ================================================================
    echo.
    echo No se encontraron configuraciones de inicio automático
    echo para el Sistema POS Avanzado.
    echo.
    pause
    exit /b 0
)

echo ================================================================
echo                     CONFIGURACIONES ENCONTRADAS
echo ================================================================
echo.
echo Se procederá a eliminar todas las configuraciones de inicio
echo automático del Sistema POS Avanzado.
echo.

set /p CONFIRM=¿Continuar con la desinstalación? (S/N): 

if /i not "%CONFIRM%"=="S" (
    echo.
    echo [CANCELADO] Desinstalación cancelada por el usuario
    pause
    exit /b 0
)

echo.
echo [INFO] Iniciando desinstalación...

REM Eliminar acceso directo
if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    if exist "%SHORTCUT_PATH%" (
        echo [ERROR] No se pudo eliminar: %SHORTCUT_PATH%
    ) else (
        echo [OK] Acceso directo eliminado
    )
)

REM Eliminar entrada de registro
reg query "%KEY_PATH%" /v "%VALUE_NAME%" >nul 2>&1
if errorlevel 0 (
    reg delete "%KEY_PATH%" /v "%VALUE_NAME%" /f >nul 2>&1
    if errorlevel 0 (
        echo [OK] Entrada de registro eliminada
    ) else (
        echo [ERROR] No se pudo eliminar entrada de registro
    )
)

echo.
echo ================================================================
echo                   DESINSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo El Sistema POS Avanzado ya NO se iniciará automáticamente
echo al arrancar Windows.
echo.
echo Para volver a activar el inicio automático:
echo - Ejecuta: install_autostart.bat
echo.
echo ================================================================
echo.
pause
exit /b 0