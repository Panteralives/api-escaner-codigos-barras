@echo off
REM ================================================================
REM Script para configurar inicio automático - Inventario Barras
REM Debe ejecutarse como Administrador
REM ================================================================

title Configurar Inicio Automático - Inventario Barras
color 0E

echo.
echo ===================================================
echo   CONFIGURAR INICIO AUTOMÁTICO - INVENTARIO BARRAS
echo ===================================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    echo Instrucciones:
    echo 1. Haz clic derecho en este archivo
    echo 2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo [%time%] Configurando inicio automático...

REM Obtener la ruta actual
set CURRENT_DIR=%~dp0
set SCRIPT_PATH=%CURRENT_DIR%start_production.bat

echo Ruta del script: %SCRIPT_PATH%

REM Verificar que el script existe
if not exist "%SCRIPT_PATH%" (
    echo ERROR: No se encuentra start_production.bat
    pause
    exit /b 1
)

REM Crear entrada en el registro de Windows
echo [%time%] Agregando entrada al registro...

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "InventarioBarras" /t REG_SZ /d "\"%SCRIPT_PATH%\"" /f

if errorlevel 1 (
    echo ERROR: No se pudo agregar la entrada al registro
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   CONFIGURACIÓN COMPLETADA EXITOSAMENTE
echo ===================================================
echo.
echo El sistema de inventario se iniciará automáticamente
echo cuando Windows arranque.
echo.
echo Para DESACTIVAR el inicio automático:
echo 1. Presiona Win + R
echo 2. Escribe: msconfig
echo 3. Ve a la pestaña "Inicio"
echo 4. Desmarca "InventarioBarras"
echo.
echo Alternativamente, ejecuta:
echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "InventarioBarras" /f
echo.

echo Presiona cualquier tecla para continuar...
pause >nul

REM Preguntar si desea probar el script ahora
echo.
set /p RESPUESTA=¿Deseas probar el script de inicio ahora? (S/N): 

if /i "%RESPUESTA%"=="S" (
    echo.
    echo [%time%] Ejecutando script de producción...
    call "%SCRIPT_PATH%"
) else (
    echo.
    echo Configuración completada. El sistema se iniciará automáticamente en el próximo reinicio.
)

echo.
pause