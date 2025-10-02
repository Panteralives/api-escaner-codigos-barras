@echo off
chcp 65001 >nul 2>&1
REM ================================================================
REM SISTEMA POS AVANZADO - INICIO AUTOMATICO OPTIMIZADO
REM ================================================================
REM Script batch para inicio automatico en Windows
REM Inicia el sistema completo y abre la interfaz lista para trabajar
REM 
REM Autor: Claude AI Assistant
REM Fecha: 01 de Octubre, 2025
REM ================================================================

REM Configurar ventana
title Sistema POS Avanzado - Inicio Automatico
color 0A

REM Ocultar ventana de comandos después de 5 segundos
if "%1"=="hidden" goto :start_hidden
if "%1"=="auto" (
    start "" /min "%~f0" hidden
    exit
)

:start_hidden
REM Cambiar al directorio del proyecto
cd /d "C:\InventarioBarras"

REM Verificar que estemos en el directorio correcto
if not exist "autostart_pos_system.py" (
    echo Error: Script de autostart no encontrado
    echo Directorio: %CD%
    pause
    exit /b 1
)

REM Mostrar mensaje de inicio (solo si no es automatico)
if not "%1"=="hidden" (
    echo.
    echo ================================================================
    echo                  SISTEMA POS AVANZADO
    echo                   INICIO AUTOMATICO
    echo ================================================================
    echo.
    echo [%time%] Iniciando sistema completo...
    echo [%time%] Backend API + Frontend Web + Interfaz lista
    echo.
    echo NOTA: Esta ventana se minimizara automaticamente.
    echo       El sistema se abrira en el navegador cuando este listo.
    echo.
    echo ================================================================
    echo.
)

REM Ejecutar el script Python de autostart
echo [%time%] Ejecutando script de inicio automatico...
python autostart_pos_system.py

REM Si llegamos aqui, el script termino
if errorlevel 1 (
    echo.
    echo ================================================================
    echo                        ERROR
    echo ================================================================
    echo.
    echo El sistema no pudo iniciarse correctamente.
    echo.
    echo Posibles soluciones:
    echo 1. Verificar que Python este instalado: python --version
    echo 2. Instalar dependencias: pip install -r requirements.txt
    echo 3. Verificar que los archivos del proyecto esten completos
    echo.
    echo ================================================================
    echo.
    if not "%1"=="hidden" pause
) else (
    echo.
    echo [%time%] Sistema cerrado correctamente
    if not "%1"=="hidden" pause
)

exit /b %errorlevel%